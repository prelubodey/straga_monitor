# Используем современную версию Python
FROM python:3.11-slim

# Настраиваем часовой пояс
ENV TZ="Europe/Moscow"

# Устанавливаем рабочую директорию
WORKDIR /app

# Устанавливаем зависимости
RUN pip install --no-cache-dir google-genai requests python-dotenv schedule pytz

# Копируем код в контейнер
COPY . .

# Запускаем скрипт
CMD ["python", "st.py"]