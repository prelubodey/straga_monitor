import imaplib, email, requests, os, time, schedule, ssl
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
        
        try:
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
                    prompt = (
                        "Analyze the patrol report and extract the following information strictly in this format. The output MUST be in Russian:\n"
                        "Период отчета: [Time period, convert dates to DD.MM.YYYY hh:mm:ss format, e.g.: 04.10.2025 09:00:00 - 05.10.2025 09:00:00]\n"
                        "Город: [Object name from the header, e.g.: Симферополь]\n"
                        "Запланировано обходов: [Number of scheduled patrols]\n"
                        "Выполнено обходов: [Number of completed patrols]\n"
                        "Нарушений: [Number of violations]\n\n"
                        "ATTENTION: Finding violations.\n"
                        "Find the table named 'Стандартный отчет по объекту' (Standard object report). Find all rows in it that have NO data in the last column (where the actual patrol time should be, usually in DD/MM/YYYY HH:MM format).\n"
                        "For each such row (where the guard arrival time is missing), extract:\n"
                        "1. Tag name / Название метки (e.g., 'Калитка буфет').\n"
                        "2. Start time / Время начала (extract ONLY hours and minutes, e.g., 04:00).\n"
                        "3. End time / Время окончания (extract ONLY hours and minutes, e.g., 04:30).\n"
                        "If 'Нарушений: 0', stop here.\n"
                        "If there are violations ('Нарушений: > 0'), you MUST output the list of violations in the following format:\n"
                        "- [Tag name]: [Start time] - [End time]\n\n"
                        "Example:\n"
                        "- Калитка буфет: 04:00 - 04:30\n\n"
                        "Write strictly according to the template, no extra words, NO dates in the violations list. Ensure the final output is in Russian."
                    )
                    
                    response = client.models.generate_content(
                        model="gemini-2.5-flash",
                        contents=[
                            types.Part.from_bytes(data=pdf_data, mime_type='application/pdf'),
                            prompt
                        ]
                    )
                    
                    # 5. Отправка в Telegram
                    text = response.text.strip()
                    tg_resp = requests.post(f"https://api.telegram.org/bot{os.getenv('TELEGRAM_BOT_TOKEN')}/sendMessage", 
                                  data={'chat_id': os.getenv('TELEGRAM_CHAT_ID'), 'text': text})
                    
                    if tg_resp.status_code == 200:
                        print(f"Готово: Отчет отправлен в Telegram.")
                    else:
                        print(f"Ошибка отправки в Telegram: {tg_resp.text}")
                    break
        finally:
            # Гарантируем закрытие соединения при любой ошибке
            mail.logout()
            
    except Exception as e:
        print(f"Ошибка подключения: {e}")

# Планировщик
schedule.every().day.at("09:10", "Europe/Moscow").do(process_last_email)

if __name__ == "__main__":
    print("Бот запущен...")
    while True:
        schedule.run_pending()
        time.sleep(30)
