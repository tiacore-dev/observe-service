from datetime import datetime
import logging


def add_text(message, text):
    from app.database.managers.user_manager import UserManager
    from app.database.managers.message_manager import MessageManager
    db_u = UserManager()
    db = MessageManager()
    user_id = message.get('user_id')
    chat_id = message.get('chat_id')

    # Преобразуем timestamp из Unix в datetime
    timestamp = datetime.fromtimestamp(message.get('timestamp'))

    logging.info(f"""Получено сообщение от пользователя {
                 user_id} в чате {chat_id}.""")

    try:
        # Проверяем, есть ли пользователь в базе
        if not db_u.user_exists(user_id):
            db_u.add_user(user_id)

        # Добавляем сообщение в базу
        db.add_message(
            timestamp=timestamp,
            user_id=user_id,
            chat_id=chat_id,
            text=text,
            s3_key=None
        )
        logging.info(f"""Сообщение от пользователя {
                     user_id} успешно записано в базу.""")
    except Exception as e:
        logging.error(
            f"Ошибка при записи сообщения от пользователя {user_id}: {e}")


def add_file(message, file_name):
    from app.database.managers.user_manager import UserManager
    from app.database.managers.message_manager import MessageManager
    db_u = UserManager()
    db = MessageManager()
    user_id = message.get('user_id')
    chat_id = message.get('chat_id')
    text = message.get('caption')
    # Преобразуем timestamp из Unix в datetime
    timestamp = datetime.fromtimestamp(message.get('timestamp'))
    try:
        # Проверяем, есть ли пользователь в базе
        if not db_u.user_exists(user_id):
            db_u.add_user(user_id)

        # Добавляем сообщение в базу
        db.add_message(
            timestamp=timestamp,
            user_id=user_id,
            chat_id=chat_id,
            text=text,
            s3_key=file_name
        )
        logging.info(f"""Сообщение от пользователя {
                     user_id} успешно записано в базу.""")
    except Exception as e:
        logging.error(
            f"Ошибка при записи сообщения от пользователя {user_id}: {e}")
