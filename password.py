import os
from dotenv import load_dotenv
from app.database import init_db, set_db_globals

load_dotenv()

password=os.getenv('PASSWORD')
login=os.getenv('LOGIN')
database_url = os.getenv('DATABASE_URL')
username='admin'
engine, Session, Base = init_db(database_url)

    # Установка глобальных переменных для работы с базой данных
set_db_globals(engine, Session, Base)


from app.database.managers.admin_manager import AdminManager
db = AdminManager()


if not db.user_exists(login):
    db.add_admin(login, username, password)
    print('New admin added successfully')

