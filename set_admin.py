import os
from dotenv import load_dotenv

load_dotenv()


def set_admin():

    from app.database.managers.admin_manager import AdminManager
    db = AdminManager()
    password = os.getenv('PASSWORD')
    login = os.getenv('LOGIN')

    username = 'admin'
    if not db.user_exists(login):
        db.add_admin(username, login, password)
        print('New admin added successfully')
