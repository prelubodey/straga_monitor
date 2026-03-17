#!/bin/bash
echo "🚀 Установка Straga Monitor..."

# 1. Проверка Docker
if ! command -v docker &> /dev/null; then
    curl -fsSL https://get.docker.com -o get-docker.sh && sh get-docker.sh
fi

# 2. Подготовка директории
PROJECT_DIR="/root/projects/straga_monitor"
rm -rf "$PROJECT_DIR"
mkdir -p "$PROJECT_DIR"
cd "$PROJECT_DIR"

# 3. Клонирование репозитория
echo "📥 Клонирование кода с GitHub..."
git clone https://github.com/prelubodey/straga_monitor.git .

# 4. Запрос личных данных
echo "📝 Введите ваши данные для настройки:"
read -p "Введите EMAIL_USER (ваш логин): " email_user </dev/tty
read -p "Введите EMAIL_PASS (ваш пароль): " email_pass </dev/tty
read -p "Введите GEMINI_API_KEY: " gemini_key </dev/tty
read -p "Введите TELEGRAM_BOT_TOKEN: " tg_token </dev/tty
read -p "Введите TELEGRAM_CHAT_ID: " chat_id </dev/tty

# 5. Формирование .env (сервер и отправитель уже в коде, здесь их не пишем)
cat <<EOF > .env
EMAIL_USER=$email_user
EMAIL_PASS=$email_pass
GEMINI_API_KEY=$gemini_key
TELEGRAM_BOT_TOKEN=$tg_token
TELEGRAM_CHAT_ID=$chat_id
EOF

# 6. Запуск
echo "🏗 Сборка и запуск контейнера..."
docker compose up -d --build

echo "✅ Мониторинг запущен!"
