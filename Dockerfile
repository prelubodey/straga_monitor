# Используем современную версию Python
FROM python:3.11-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Устанавливаем зависимости (включая schedule и pytz)
RUN pip install --no-cache-dir google-genai requests python-dotenv schedule pytz

# Копируем код в контейнер
COPY . .

# Запускаем скрипт
CMD ["python", "st.py"]