import os

import psycopg2
from dotenv import load_dotenv

# Загружаем переменные из .env
load_dotenv()

def get_connection():
    """Подключение к БД."""
    db_config = {
        'host': os.getenv("DB_HOST"),
        'port': os.getenv("DB_PORT"),
        'dbname': os.getenv("DB_NAME"),
        'user': os.getenv("DB_USER"),
        'password': os.getenv("DB_PASSWORD"),
        'client_encoding': 'UTF8'
    }
    return psycopg2.connect(**db_config)


def get_version_from_schema_migrations(cursor):
    """Получает значение version из таблицы schema_migrations."""
    cursor.execute("SELECT version FROM schema_migrations LIMIT 1;")
    result = cursor.fetchone()
    if result:
        return result[0]
    else:
        raise Exception("Не найдена запись в таблице schema_migrations")
