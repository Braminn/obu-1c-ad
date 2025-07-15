Для работы скрипта, необходиму установить uv

`sudo dnf install libpq-devel` - чтобы установился psycopg2 для работы с БД

Создать файл .env с содержимым
```
DB_HOST=
DB_PORT=
DB_NAME=
DB_USER=
DB_PASSWORD=
EXPORT_DIR=
```

`uv run ./src/obu_1c-ad/main.py` - запуск скрипта через uv

Для удобства запуска через cron или CI/CD можно использовать запуск через run.sh