import os
from dotenv import load_dotenv

load_dotenv()


# Константы API
YANDEX_SPEECHKIT_API_URL = os.getenv('YANDEX_SPEECHKIT_API_URL')
YANDEX_GPT_API_URL = os.getenv('YANDEX_GPT_API_URL')

# Токен и ID каталога
YANDEX_API_KEY = os.getenv('YANDEX_API_KEY')
FOLDER_ID = os.getenv('FOLDER_ID')
