from dotenv import load_dotenv
import os

# Определяем путь к .env (он лежит в корне проекта)
dotenv_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "./.env"))
load_dotenv(dotenv_path)  # Загружаем переменные

from os import getenv

# Переменные для календаря
TYPE = getenv('TYPE')
PROJECT_ID = getenv('PROJECT_ID')
PRIVATE_ID_KEY = getenv('PRIVATE_ID_KEY')
PRIVATE_KEY = getenv('PRIVATE_KEY')
CLIENT_EMAIL = getenv('CLIENT_EMAIL')
CLIENT_ID = getenv('CLIENT_ID')
AUTH_URI = getenv('AUTH_URI')
TOKEN_URI = getenv('TOKEN_URI')
AUTH_PROVIDER_X509_CERT_URL = getenv('AUTH_PROVIDER_X509_CERT_URL')
CLIENT_X509_CERT_URL = getenv('CLIENT_X509_CERT_URL')
UNIVERSE_DOMAIN = getenv('UNIVERSE_DOMAIN')

CREDENTIALS = {"type": TYPE,
  "project_id": PROJECT_ID,
  "private_key_id": PRIVATE_ID_KEY,
  "private_key": PRIVATE_KEY.replace("\\n", "\n"),
  "client_email": CLIENT_EMAIL,
  "client_id": CLIENT_ID,
  "auth_uri": AUTH_URI,
  "token_uri": TOKEN_URI,
  "auth_provider_x509_cert_url": AUTH_PROVIDER_X509_CERT_URL,
  "client_x509_cert_url": CLIENT_X509_CERT_URL,
  "universe_domain": UNIVERSE_DOMAIN
}

GENERAL_CALENDAR_ID = getenv('GENERAL_CALENDAR_ID')
PERSONAL_CALENDAR_ID = getenv('PERSONAL_CALENDAR_ID')

# Путь к хранилищу Obsidian
VAULT_PATH = getenv('VAULT_PATH')

# Файл для хранения информации о последнем выполнении
LAST_RUN_FILE = getenv('LAST_RUN_FILE')

# Путь к файлу с регулярными тасками
REGULAR_PATH_FILE = getenv('REGULAR_PATH_FILE')

# Путь к папке с задачами в Obsidian
TASKS_PATH = getenv('TASKS_PATH')

# Дата последнего запуска файла
LAST_DATE = getenv("MY_DATE")
