# -*- coding: utf-8 -*-
import imaplib, email, requests, os, time, schedule, ssl, logging
from datetime import datetime
from google import genai
from dotenv import load_dotenv

# Загружаем переменные из .env в папке со скриптом
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("straga_monitor")

# Инициализация Gemini
gemini_key = os.getenv('GEMINI_API_KEY')
if not gemini_key:
    logger.error("ERROR: GEMINI_API_KEY is missing in .env file!")
    exit(1)

client = genai.Client(api_key=gemini_key)

def process_daily_emails():
    logger.info("Проверка почты за текущие сутки...")
    
    # Отключаем строгую проверку SSL для корпоративных серверов
    context = ssl.create_default_context()
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE

    try:
        # 1. Подключение
        email_user = os.getenv('EMAIL_USER')
        email_pass = os.getenv('EMAIL_PASS')
        
        if not email_user or not email_pass:
            logger.error("ОШИБКА: EMAIL_USER или EMAIL_PASS не найдены в .env!")
            return

        mail = imaplib.IMAP4_SSL("mail.rbauto.ru", 993, ssl_context=context)
        mail.login(email_user, email_pass)
        
        try:
            mail.select("INBOX")
            
            # 2. Поиск писем от otchet@straga.ru за СЕГОДНЯ
            today_str = datetime.now().strftime("%d-%b-%Y")
            search_query = f'(FROM "otchet@straga.ru" SINCE {today_str})'
            
            status, messages = mail.search(None, search_query)
            if not messages[0]:
                logger.info("Писем от otchet@straga.ru за сегодня нет.")
                return

            email_ids = messages[0].split()
            logger.info(f"Найдено {len(email_ids)} писем за сегодня. Начинаю обработку...")

            # 3. Обработка КАЖДОГО письма
            for email_id in email_ids:
                _, data = mail.fetch(email_id, '(RFC822)')
                msg = email.message_from_bytes(data[0][1])

                for part in msg.walk():
                    filename = part.get_filename()
                    if filename and filename.lower().endswith('.pdf'):
                        logger.info(f"Анализирую файл: {filename}")
                        pdf_data = part.get_payload(decode=True)
                        
                        # 4. Анализ ИИ
                        prompt = (
                            "Analyze the patrol report and extract the following information strictly in this format. The output MUST be in Russian:\n"
                            "Город: [Object name from the header, e.g.: Симферополь]\n"
                            "Период отчета: [Time period, convert dates to DD.MM.YYYY hh:mm:ss format, e.g.: 04.10.2025 09:00:00 - 05.10.2025 09:00:00]\n"
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
                        
                        try:
                            response = client.models.generate_content(
                                model='gemini-2.5-flash-lite',
                                contents=[
                                    genai.types.Part.from_bytes(data=pdf_data, mime_type='application/pdf'),
                                    prompt
                                ],
                                config=genai.types.GenerateContentConfig(
                                    temperature=0
                                )
                            )
                            
                            report_text = f"ОТЧЕТ ОБХОДОВ\n\n{response.text.strip()}"

                            # Отправка в MAX
                            max_token = os.getenv('MAX_BOT_TOKEN')
                            max_chat = os.getenv('MAX_CHAT_ID')
                            
                            max_resp = requests.post(
                                "https://platform-api.max.ru/messages",
                                params={
                                    "v": "1.0.0",
                                    "chat_id": int(max_chat)
                                },
                                headers={
                                    "Authorization": max_token,
                                    "Content-Type": "application/json"
                                },
                                json={
                                    "text": report_text,
                                    "attachments": [],
                                    "link": None,
                                    "format": "markdown"
                                },
                                timeout=15
                            )

                            if max_resp.status_code == 200:
                                logger.info(f"Success! Report {filename} sent to MAX.")
                            else:
                                logger.error(f"MAX API Error {max_resp.status_code}: {max_resp.text}")

                        except Exception as e:
                            logger.error(f"Gemini/MAX Error: {e}")
        
        finally:
            mail.logout()
    except Exception as e:
        logger.error(f"General Error: {e}")

# Запуск раз в день
schedule.every().day.at("09:10").do(process_daily_emails)

if __name__ == "__main__":
    logger.info("Straga Monitor started. Running immediate test...")
    process_daily_emails()
    
    logger.info("Test finished. Waiting for schedule at 09:10...")
    while True:
        schedule.run_pending()
        time.sleep(30)
