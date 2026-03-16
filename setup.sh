#!/bin/bash

echo "------------------------------------------------"
echo "🚀 Начинаю установку окружения для ботов..."
echo "------------------------------------------------"

# 1. Обновление системы
sudo apt-get update && sudo apt-get upgrade -y

# 2. Установка Docker
if ! command -v docker &> /dev/null
then
    echo "📦 Устанавливаю Docker..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
    sudo usermod -aG docker $USER
else
    echo "✅ Docker уже установлен."
fi

# 3. Создание структуры папок
mkdir -p /root/projects
cd /root/projects

# 4. Клонирование репозиториев
echo "git Клонирую проекты..."
git clone https://github.com/prelubodey/buhgalter_kds.git
git clone https://github.com/prelubodey/straga_monitor.git

echo "------------------------------------------------"
echo "✅ УСТАНОВКА ЗАВЕРШЕНА УСПЕШНО!"
echo "------------------------------------------------"
echo "⚠️  ВНИМАНИЕ: НЕОБХОДИМО ВЫПОЛНИТЬ СЛЕДУЮЩИЕ ШАГИ:"
echo ""
echo "1. Создать файлы .env в директориях:"
echo "   - /root/projects/buhgalter_kds/.env"
echo "   - /root/projects/straga_monitor/.env"
echo ""
echo "2. Создать файл docker-compose.yml в директории:"
echo "   - /root/projects/docker-compose.yml"
echo ""
echo "3. После добавления файлов запустите ботов командой:"
echo "   cd /root/projects && docker compose up -d --build"
echo "------------------------------------------------"