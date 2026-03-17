Установка

curl -sSL https://raw.githubusercontent.com/prelubodey/straga_monitor/main/setup.sh | bash

Проверка работоспособности

docker exec -it straga-ai-monitor python3 -u -c "from st import process_last_email; process_last_email()"
