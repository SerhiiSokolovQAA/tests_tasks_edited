import os
import sys
import importlib.util

# Путь к корню проекта
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)

# Путь к файлу с парсером
module_path = os.path.join(BASE_DIR, "modules", "3_selenium_model.py")

# Динамическая загрузка модуля
spec = importlib.util.spec_from_file_location("selenium_model", module_path)
selenium_model = importlib.util.module_from_spec(spec)
spec.loader.exec_module(selenium_model)


if __name__ == "__main__":
    selenium_model.selenium_parser()
