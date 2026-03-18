#!/bin/bash
echo "🚀 Установка Straga Monitor..."

# 1. Установка Docker (если нет)
if ! command -v docker &> /dev/null; then
    curl -fsSL https://get.docker.com -o get-docker.sh && sh get-docker.sh
fi

# 2. Очистка и подготовка папки
PROJECT_DIR="/root/projects/straga_monitor"
rm -rf "$PROJECT_DIR"
mkdir -p "$PROJECT_DIR"
cd "$PROJECT_DIR"

# 3. Клонирование репозитория
echo "📥 Загрузка кода с GitHub..."
git clone https://github.com/prelubodey/straga_monitor.git .

# 4. Запрос данных (сервер и отправитель зашиты в коде, их не спрашиваем)
echo "📝 Настройка доступа..."
read -p "Введите ваш EMAIL_USER (логин): " email_user </dev/tty
read -p "Введите ваш EMAIL_PASS (пароль): " email_pass </dev/tty
read -p "Введите ваш GEMINI_API_KEY: " gemini_key </dev/tty
read -p "Введите ваш TELEGRAM_BOT_TOKEN: " tg_token </dev/tty
read -p "Введите ваш TELEGRAM_CHAT_ID: " chat_id </dev/tty
read -p "Введите ваш MAX_BOT_TOKEN (опционально, если есть): " max_token </dev/tty
read -p "Введите ваш MAX_CHAT_ID (ID чата в МАКС, опционально): " max_chat_id </dev/tty

# 5. Создание .env с ПРАВИЛЬНЫМИ именами переменных для st.py
cat <<EOF > .env
EMAIL_USER=$email_user
EMAIL_PASS=$email_pass
GEMINI_API_KEY=$gemini_key
TELEGRAM_BOT_TOKEN=$tg_token
TELEGRAM_CHAT_ID=$chat_id
MAX_BOT_TOKEN=$max_token
MAX_CHAT_ID=$max_chat_id
EOF

# 6. Запуск через Docker Compose
echo "🏗 Сборка и запуск контейнера..."
docker compose up -d --build

echo "✅ Установка завершена! Бот запущен."
