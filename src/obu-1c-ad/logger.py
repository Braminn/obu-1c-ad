import logging
import os

# Настройка логирования
log_dir = "logs"
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, "obu-1c-ad.log")

# Создаём логгер
logger = logging.getLogger("obu_1c_ad")
logger.setLevel(logging.INFO)

# Формат логов
log_format = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s', 
                               datefmt='%Y-%m-%d %H:%M:%S')

# Обработчик для файла
file_handler = logging.FileHandler(log_file, encoding='utf-8')
file_handler.setFormatter(log_format)
logger.addHandler(file_handler)

# Обработчик для консоли
console_handler = logging.StreamHandler()
console_handler.setFormatter(log_format)
logger.addHandler(console_handler)
