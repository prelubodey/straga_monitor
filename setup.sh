#!/bin/bash
echo "?? Обновление конфигурации Straga Monitor..."

PROJECT_DIR="/root/projects/straga_monitor"
mkdir -p "$PROJECT_DIR"
cd "$PROJECT_DIR"

# Проверка наличия docker-compose.yml и других необходимых файлов
if [ ! -f "docker-compose.yml" ] || [ ! -f "Dockerfile" ] || [ ! -f "st.py" ]; then
    echo "? Файлы проекта отсутствуют. Скачиваю из GitHub..."
    
    # Скачиваем файлы из репозитория
    FILES=("docker-compose.yml" "Dockerfile" "st.py" ".gitignore" "README.md")
    REPO_RAW_URL="https://raw.githubusercontent.com/prelubodey/straga_monitor/main"

    for file in "${FILES[@]}"; do
        echo "Скачивание $file..."
        curl -sSL "$REPO_RAW_URL/$file" -o "$file"
    done
fi

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
