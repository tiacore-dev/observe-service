# autopep8: off
import eventlet # pylint: disable=import-error
eventlet.monkey_patch()

import os # pylint: disable=wrong-import-position
from dotenv import load_dotenv # pylint: disable=wrong-import-position
from app import create_app # pylint: disable=wrong-import-position
# autopep8: on
load_dotenv()

# Получаем порт из переменных окружения
port = os.getenv('FLASK_PORT', '5000')

# Создаем приложение
app = create_app('Development')

# Запускаем приложение
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=port, debug=True)
