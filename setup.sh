#!/bin/bash
echo "🚀 Установка Straga Monitor..."

# 1. Проверка Docker
if ! command -v docker &> /dev/null; then
    curl -fsSL https://get.docker.com -o get-docker.sh && sh get-docker.sh
fi

# 2. Подготовка директории
PROJECT_DIR="/root/projects/straga_monitor"
rm -rf "$PROJECT_DIR" # Удаляем старую папку, чтобы клон прошел чисто
mkdir -p "$PROJECT_DIR"
cd "$PROJECT_DIR"

# 3. Клонирование репозитория
echo "📥 Клонирование кода с GitHub..."
git clone https://github.com/prelubodey/straga_monitor.git .

# 4. Запрос данных для .env (используем имена, которые ожидает код)
echo "📝 Настройка конфигурации..."
read -p "Введите IMAP_SERVER (например, mail.rbauto.ru): " imap_server </dev/tty
read -p "Введите EMAIL_USER (ваш логин): " email_user </dev/tty
read -p "Введите EMAIL_PASS (пароль): " email_pass </dev/tty
read -p "Введите SENDER_EMAIL (от кого ждем отчеты): " sender_email </dev/tty
read -p "Введите GEMINI_API_KEY: " gemini_key </dev/tty
read -p "Введите TELEGRAM_BOT_TOKEN: " tg_token </dev/tty
read -p "Введите TELEGRAM_CHAT_ID: " chat_id </dev/tty

# 5. Формирование .env файла с ПРАВИЛЬНЫМИ ключами
cat <<EOF > .env
IMAP_SERVER=$imap_server
EMAIL_USER=$email_user
EMAIL_PASS=$email_pass
SENDER_EMAIL=$sender_email
GEMINI_API_KEY=$gemini_key
TELEGRAM_BOT_TOKEN=$tg_token
TELEGRAM_CHAT_ID=$chat_id
EOF

# 6. Создание docker-compose.yml (если его нет в репозитории)
cat <<EOF > docker-compose.yml
services:
  straga_monitor:
    build: .
    container_name: straga-ai-monitor
    restart: always
    env_file: .env
EOF

# 7. Запуск проекта
echo "🏗 Сборка и запуск контейнера..."
docker compose up -d --build

echo "✅ Мониторинг успешно запущен!"
docker ps | grep straga-ai-monitor

docker compose up -d --build
echo "✅ Мониторинг запущен!"
