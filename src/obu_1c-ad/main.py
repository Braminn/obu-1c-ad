import psycopg2
import csv
import os
from dotenv import load_dotenv
from datetime import datetime

# Загрузка переменных окружения
load_dotenv()

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
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor()
        
        # Получаем версию для имени файла
        version = get_version_from_schema_migrations(cursor)
        today = datetime.today().strftime('%Y-%m-%d')

        # Получение пути из переменной окружения
        export_dir = os.getenv("EXPORT_DIR", "data")
        print(export_dir)

        # Создание папки, если её нет
        os.makedirs(export_dir, exist_ok=True)

        # Формируем имя файла с дефисом между датой и версией
        filename = f"{today}-{version}.csv"

        # Полный путь к файлу
        output_file = os.path.join(export_dir, filename)
        print(f"Экспорт будет выполнен в: {os.path.abspath(output_file)}")
        
        # SQL-запрос с добавлением inn перед company_id
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
        LEFT JOIN departments d ON w.department_id = d.id;
        """
        cursor.execute(query)
        column_names = [desc[0] for desc in cursor.description]

        with open(output_file, mode='w', newline='', encoding='utf-8-sig') as file:
            writer = csv.writer(file)
            writer.writerow(column_names)
            writer.writerows(cursor.fetchall())

        print(f"Данные успешно экспортированы в {output_file}")

    except Exception as e:
        print(f"Ошибка: {e}")

    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    export_workplaces_to_csv()