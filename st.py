import imaplib, email, requests, os, time, schedule, ssl, pytz
from datetime import datetime
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

# Инициализация клиентов
client = genai.Client(api_key=os.getenv('GEMINI_API_KEY'))

def process_last_email():
    print(f"[{datetime.now()}] Проверка почты...")
    
    # Отключаем строгую проверку SSL для корпоративных серверов
    context = ssl.create_default_context()
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE

    try:
        # 1. Подключение и поиск
        mail = imaplib.IMAP4_SSL("mail.rbauto.ru", 993, ssl_context=context)
        mail.login(os.getenv('EMAIL_USER'), os.getenv('EMAIL_PASS'))
        mail.select("INBOX")
        
        # Ищем письма именно от otchet@straga.ru
        status, messages = mail.search(None, f'(FROM "otchet@straga.ru")')
        if not messages[0]:
            print("Писем от otchet@straga.ru нет.")
            return

        # 2. Берем последнее письмо
        last_id = messages[0].split()[-1]
        _, data = mail.fetch(last_id, '(RFC822)')
        msg = email.message_from_bytes(data[0][1])

        # 3. Поиск PDF во вложениях
        for part in msg.walk():
            filename = part.get_filename()
            if filename and filename.lower().endswith('.pdf'):
                print(f"Анализирую: {filename}")
                pdf_data = part.get_payload(decode=True)
                
                # 4. Анализ ИИ
                response = client.models.generate_content(
                    model="gemini-2.5-flash-lite",
                    contents=[
                        types.Part.from_bytes(data=pdf_data, mime_type='application/pdf'),
                        "Проанализируй отчет. Если нарушений нет, ответь 'Нарушений нет'. Если есть — кратко перечисли их."
                    ]
                )
                
                # 5. Отправка в Telegram
                text = response.text.strip()
                requests.post(f"https://api.telegram.org/bot{os.getenv('TELEGRAM_BOT_TOKEN')}/sendMessage", 
                              data={'chat_id': os.getenv('TELEGRAM_CHAT_ID'), 'text': text})
                print(f"Готово: {text}")
                break
        
        mail.logout()
    except Exception as e:
        print(f"Ошибка: {e}")

# Планировщик
schedule.every().day.at("09:10", "Europe/Moscow").do(process_last_email)

if __name__ == "__main__":
    print("Бот запущен...")
    while True:
        schedule.run_pending()
        time.sleep(30)
