FROM python:3.11-slim
ENV TZ="Europe/Moscow"
WORKDIR /app
# Добавлены pytz и requests, если их не было
RUN pip install --no-cache-dir google-genai requests python-dotenv schedule pytz
COPY . .
CMD ["python", "st.py"]
