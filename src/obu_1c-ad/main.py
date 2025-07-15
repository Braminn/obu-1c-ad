import psycopg2
import csv
import os
import logging
from dotenv import load_dotenv
from datetime import datetime

# Загрузка переменных окружения
load_dotenv()

# Настройка логирования
log_dir = "logs"
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, "obu-1c-ad.log")

# Создаём логгер
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Формат логов
log_format = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

# Файл-обработчик
file_handler = logging.FileHandler(log_file, encoding='utf-8')
file_handler.setFormatter(log_format)
logger.addHandler(file_handler)

# Обработчик для консоли
console_handler = logging.StreamHandler()
console_handler.setFormatter(log_format)
logger.addHandler(console_handler)


def get_version_from_schema_migrations(cursor):
    """Получает значение version из таблицы schema_migrations."""
    cursor.execute("SELECT version FROM schema_migrations LIMIT 1;")
    result = cursor.fetchone()
    if result:
        return result[0]
    else:
        raise Exception("Не найдена запись в таблице schema_migrations")


def export_workplaces_to_csv():
    db_config = {
        'host': os.getenv("DB_HOST"),
        'port': os.getenv("DB_PORT"),
        'dbname': os.getenv("DB_NAME"),
        'user': os.getenv("DB_USER"),
        'password': os.getenv("DB_PASSWORD"),
        'client_encoding': 'UTF8'
    }
    
    try:
        logger.info("Попытка подключения к базе данных...")
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor()
        logger.info("Подключение к базе данных успешно")
        
        # Получаем версию для имени файла
        version = get_version_from_schema_migrations(cursor)
        today = datetime.today().strftime('%Y-%m-%d')

        # Получение пути из переменной окружения
        export_dir = os.getenv("EXPORT_DIR", "data")

        # Создание папки, если её нет
        os.makedirs(export_dir, exist_ok=True)

        # Получаем формат имени файла из переменной окружения
        filename_format = os.getenv("FILENAME_FORMAT", "full").lower()

        # Выбираем имя файла в зависимости от формата
        if filename_format == "version":
            filename = f"{version}.csv"
        else:  # по умолчанию или если явно указано "full"
            filename = f"{today}-{version}.csv"

        # Полный путь к файлу
        output_file = os.path.join(export_dir, filename)
        
        logger.info(f"Файл будет сохранён в: {os.path.abspath(output_file)}")
        
        # SQL-запрос
        query = """
        SELECT 
            w.employee_id,
            e.full_name AS employee_name,
            c.name AS company_name,
            c.inn,
            w.company_id,
            p.name AS position_name,
            d.name AS department_name,
            w.workplace_type,
            w.recruit_date,
            w.retire_date
        FROM workplaces w
        LEFT JOIN companies c ON w.company_id = c.id
        LEFT JOIN employees e ON w.employee_id = e.id
        LEFT JOIN positions p ON w.position_id = p.id
        LEFT JOIN departments d ON w.department_id = d.id
        ORDER BY w.recruit_date DESC;
        """
        cursor.execute(query)
        column_names = [desc[0] for desc in cursor.description]
        data = cursor.fetchall()
        logger.info(f"Успешно получено {len(data)} записей из базы данных")

        with open(output_file, mode='w', newline='', encoding='utf-8-sig') as file:
            writer = csv.writer(file)
            writer.writerow(column_names)
            writer.writerows(data)

        logger.info(f"Файл успешно сохранён: {output_file}")

    except Exception as e:
        logger.error(f"Ошибка: {e}")

    finally:
        if 'cursor' in locals():
            cursor.close()
            logger.info("Курсор закрыт")
        if 'conn' in locals():
            conn.close()
            logger.info("Соединение с базой данных закрыто")


if __name__ == "__main__":
    export_workplaces_to_csv()
