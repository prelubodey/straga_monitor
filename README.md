Установка
```bash
curl -sSL https://raw.githubusercontent.com/prelubodey/straga_monitor/main/setup.sh | bash
```
Проверка работоспособности
```bash
docker exec -it straga-ai-monitor python3 -u -c "from st import process_last_email; process_last_email()"
```
Перейдите в папку: cd /root/projects/buhgalter_monitor

Остановить бота:
```bash
docker compose stop
```
(Контейнер сохранится, но перестанет работать).

Запустить остановленного бота:
```bash
docker compose start
```
Полностью удалить контейнер и остановить его:
```bash
docker compose down
```
Запустить с нуля (со сборкой):
```bash
docker compose up -d --build
```
