Для работы скрипта, необходимо установить *uv*.
`curl -LsSf https://astral.sh/uv/install.sh | sh`
Или смотри документацию:
https://docs.astral.sh/uv/getting-started/installation/

Чтобы установился psycopg2, нужно установить *libpq-devel*
`sudo dnf install libpq-devel`

Создать файл *.env* с содержимым
```
DB_HOST=
DB_PORT=
DB_NAME=
DB_USER=
DB_PASSWORD=
EXPORT_DIR=
FILENAME_FORMAT=full для полного имени файла или version для сокращенного
```

Запуск скрипта через uv
`uv run ./src/obu_1c-ad/main.py`

Для удобства запуска через cron или CI/CD можно использовать *run.sh* (он так же использует uv)