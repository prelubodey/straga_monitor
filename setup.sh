#!/bin/bash
echo "🚀 Установка Straga Monitor..."

if ! command -v docker &> /dev/null; then
    curl -fsSL https://get.docker.com -o get-docker.sh && sh get-docker.sh
fi

mkdir -p /root/projects/straga_monitor
cd /root/projects/straga_monitor

if [ ! -d ".git" ]; then
    git clone https://github.com/prelubodey/straga_monitor.git .
fi

# Запрос данных для .env
# Запрос данных для .env с использованием </dev/tty
read -p "Введите EMAIL_USER: " email_user </dev/tty
read -p "Введите EMAIL_PASS: " email_pass </dev/tty
read -p "Введите TELEGRAM_TOKEN: " tg_token </dev/tty
read -p "Введите CHAT_ID: " chat_id </dev/tty
read -p "Введите GEMINI_API_KEY: " gemini_key </dev/tty

cat <<EOF > .env
EMAIL_USER=$email_user
EMAIL_PASS=$email_pass
TELEGRAM_TOKEN=$tg_token
CHAT_ID=$chat_id
GEMINI_API_KEY=$gemini_key
EOF

cat <<EOF > docker-compose.yml
services:
  straga_monitor:
    build: .
    container_name: straga-ai-monitor
    restart: always
    env_file: .env
EOF

docker compose up -d --build
echo "✅ Мониторинг запущен!"
