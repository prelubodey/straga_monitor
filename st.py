import imaplib
import email
import requests
import os
import time
import schedule
import pytz
from datetime import datetime
from google import genai
from google.genai import types
from email.header import decode_header
from dotenv import load_dotenv

# Загружаем переменные из .env
load_dotenv()

# Читаем настройки из окружения
IMAP_SERVER = os.getenv('IMAP_SERVER')
EMAIL_USER = os.getenv('EMAIL_USER')
EMAIL_PASS = os.getenv('EMAIL_PASS')
SENDER_EMAIL = os.getenv('SENDER_EMAIL')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

# Инициализация клиента Gemini
client = genai.Client(api_key=GEMINI_API_KEY)

def send_telegram(text):
    """Отправка сообщения в Telegram"""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    try:
        response = requests.post(url, data={'chat_id': TELEGRAM_CHAT_ID, 'text': text})
        response.raise_for_status()
    except Exception as e:
        print(f"Ошибка отправки в Telegram: {e}")

def analyze_report_with_ai(file_data):
    """Анализ PDF через Gemini"""
    prompt = """
    Проанализируй этот отчет о патрулировании. 
    Если в отчете указано, что нарушений 0 или все обходы выполнены вовремя согласно графику, ответь строго фразой: "Нарушений по обходам нет".
    Если выявлены нарушения (пропуски, опоздания, нарушения графика), напиши: "Выявлены нарушения обходов:", укажи название метки и время начала обхода для каждого случая.
    """
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash-lite",
            contents=[
                types.Part.from_bytes(data=file_data, mime_type='application/pdf'),
                prompt
            ]
        )
        return response.text.strip()
    except Exception as e:
        return f"Ошибка при анализе ИИ: {e}"

def process_last_email():
    """Поиск письма и обработка вложения"""
    print(f"[{datetime.now()}] Начинаю проверку почты...")
    mail = imaplib.IMAP4_SSL(IMAP_SERVER)
    
    try:
        mail.login(EMAIL_USER, EMAIL_PASS)
        mail.select("INBOX")

        status, messages = mail.search(None, f'(FROM "{SENDER_EMAIL}")')
        
        if status != 'OK' or not messages[0]:
            print(f"Писем от {SENDER_EMAIL} не найдено.")
            send_telegram(f"⚠️ Отчет от {SENDER_EMAIL} не найден в почте.")
            return

        mail_ids = messages[0].split()
        last_email_id = mail_ids[-1]

        res, msg_data = mail.fetch(last_email_id, '(RFC822)')
        
        for response_part in msg_data:
            if isinstance(response_part, tuple):
                msg = email.message_from_bytes(response_part[1])
                
                for part in msg.walk():
                    if part.get_content_maintype() == 'multipart' or part.get('Content-Disposition') is None:
                        continue

                    filename = part.get_filename()
                    if filename:
                        decode_name = decode_header(filename)[0]
                        if isinstance(decode_name[0], bytes):
                            filename = decode_name[0].decode(decode_name[1] or 'utf-8')
                        
                        print(f"Обработка файла: {filename}")
                        file_content = part.get_payload(decode=True)
                        report_result = analyze_report_with_ai(file_content)
                        
                        send_telegram(report_result)
                        print(f"Результат отправлен: {report_result}")
                        return

    except Exception as e:
        error_msg = f"Критическая ошибка: {e}"
        print(error_msg)
        send_telegram(error_msg)
    finally:
        mail.logout()

def job():
    process_last_email()

if __name__ == "__main__":
    moscow_tz = pytz.timezone('Europe/Moscow')
    print("Бот запущен. Ожидание времени 09:10 по Москве...")
    
    # Планируем ежедневную задачу
    schedule.every().day.at("09:10", "Europe/Moscow").do(job)

    while True:
        schedule.run_pending()
        time.sleep(30)