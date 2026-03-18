import imaplib, email, requests, os, time, schedule, ssl, logging
from logging.handlers import RotatingFileHandler
from datetime import datetime
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

# Настройка логирования (Ограничение: ~100 KB, храним 1 старый файл)
logger = logging.getLogger("straga_monitor")
logger.setLevel(logging.INFO)

formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

# Обработчик для записи в файл
file_handler = RotatingFileHandler('app.log', maxBytes=100*1024, backupCount=1, encoding='utf-8')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# Обработчик для вывода в консоль
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

# Инициализация клиентов
client = genai.Client(api_key=os.getenv('GEMINI_API_KEY'))

def process_daily_emails():
    logger.info("Проверка почты за текущие сутки...")
    
    # Отключаем строгую проверку SSL для корпоративных серверов
    context = ssl.create_default_context()
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE

    try:
        # 1. Подключение
        mail = imaplib.IMAP4_SSL("mail.rbauto.ru", 993, ssl_context=context)
        mail.login(os.getenv('EMAIL_USER'), os.getenv('EMAIL_PASS'))
        
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
                        
                        try:
                            response = client.models.generate_content(
                                model="gemini-2.5-flash",
                                contents=[
                                    types.Part.from_bytes(data=pdf_data, mime_type='application/pdf'),
                                    prompt
                                ]
                            )
                            
                            text = response.text.strip()
                            
                            # 5. Отправка в Telegram
                            tg_resp = requests.post(f"https://api.telegram.org/bot{os.getenv('TELEGRAM_BOT_TOKEN')}/sendMessage", 
                                          data={'chat_id': os.getenv('TELEGRAM_CHAT_ID'), 'text': text})
                            
                            if tg_resp.status_code == 200:
                                logger.info(f"Отчет {filename} успешно отправлен в Telegram.")
                            else:
                                logger.error(f"Ошибка отправки {filename} в Telegram: {tg_resp.text}")
                                
                        except Exception as ai_e:
                            logger.error(f"Ошибка при анализе файла {filename} с помощью ИИ: {ai_e}")

                        # Небольшая пауза между файлами, чтобы не спамить в ТГ
                        time.sleep(2)
        finally:
            # Гарантируем закрытие соединения при любой ошибке
            mail.logout()
            logger.info("Соединение с почтовым сервером закрыто.")
            
    except Exception as e:
        logger.error(f"Ошибка подключения или работы с почтой: {e}")

# Планировщик
schedule.every().day.at("09:10", "Europe/Moscow").do(process_daily_emails)

if __name__ == "__main__":
    logger.info("Бот запущен. Ожидание задачи по расписанию...")
    while True:
        schedule.run_pending()
        time.sleep(30)
