#!/bin/bash
echo "?? Обновление конфигурации Straga Monitor..."

PROJECT_DIR="/root/projects/straga_monitor"
cd "$PROJECT_DIR"

# Запрос данных
read -p "Введите EMAIL_USER: " email_user </dev/tty
read -p "Введите EMAIL_PASS: " email_pass </dev/tty
read -p "Введите GEMINI_API_KEY: " gemini_key </dev/tty
read -p "Введите MAX_BOT_TOKEN: " max_token </dev/tty
read -p "Введите MAX_CHAT_ID: " max_chat </dev/tty

# Создание .env
cat <<EOF > .env
EMAIL_USER=$email_user
EMAIL_PASS=$email_pass
GEMINI_API_KEY=$gemini_key
MAX_BOT_TOKEN=$max_token
MAX_CHAT_ID=$max_chat
EOF

echo "? Файл .env обновлен."
echo "Пересобираю контейнер..."
docker compose up -d --build