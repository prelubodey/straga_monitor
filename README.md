Установка
```bash
curl -sSL https://raw.githubusercontent.com/prelubodey/straga_monitor/main/setup.sh | bash
```
Проверка работоспособности
```bash
docker exec -it straga-ai-monitor python3 -u -c "from st import process_last_email; process_last_email()"
```
Перейдите в папку: 
```bash
cd /root/projects/straga_monitor
```
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
Посмотреть, кто запущен	
```bash
docker ps
```
Посмотреть все контейнеры (даже выключенные)	
```bash
docker ps -a
```
Посмотреть логи в реальном времени	
```bash
docker logs -f straga-ai-monitor
```
