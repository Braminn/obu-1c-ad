# src/obu_1c_ad/exporter.py
import csv
import os
from datetime import datetime

from .database import get_connection, get_version_from_schema_migrations
from .logger import logger


def export_workplaces_to_csv():
    """Экспорт данных из БД в csv файл."""
    try:
        logger.info("Попытка подключения к базе данных...")
        conn = get_connection()
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

        # Сохраняем файл в UTF-8
        with open(output_file, mode='w', newline='', encoding='utf-8-sig') as file:
            writer = csv.writer(file, delimiter=';')
            writer.writerow(column_names)
            writer.writerows(data)
        logger.info(f"Файл успешно сохранён: {output_file}")

        # Формируем имя ANSI-файла
        output_file_ansi = os.path.splitext(output_file)[0] + "_ANSI.csv"
        
        # Сохраняем файл в ANSI (Windows-1251)
        try:
            with open(output_file_ansi, mode='w', newline='', encoding='cp1251') as file:  # noqa: E501
                writer = csv.writer(file, delimiter=';')
                writer.writerow(column_names)
                writer.writerows(data)
            logger.info(f"Файл успешно сохранён (ANSI): {output_file_ansi}")
        except UnicodeEncodeError as e:
            logger.error(f"Ошибка кодировки при сохранении ANSI-файла: {e}")

    except Exception as e:
        logger.error(f"Ошибка: {e}")

    finally:
        if 'cursor' in locals():
            cursor.close()
            logger.info("Курсор закрыт")
        if 'conn' in locals():
            conn.close()
            logger.info("Соединение с базой данных закрыто")
