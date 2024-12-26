import logging


def sync_chats_from_messages(bot):
    """
    Находит уникальные chat_id в таблице messages и добавляет их в таблицу chats,
    используя Telegram API для получения названия чатов.
    """
    from app.database.managers.chat_manager import ChatManager
    from app.database.managers.message_manager import MessageManager
    # Менеджеры
    chat_manager = ChatManager()
    message_manager = MessageManager()
    # Получаем все уникальные chat_id из таблицы messages
    messages = message_manager.get_filtered_messages()
    unique_chat_ids = {message.chat_id for message in messages}

    for chat_id in unique_chat_ids:
        # Проверяем, есть ли chat_id в таблице chats
        existing_chat = chat_manager.get_chat_by_id(chat_id)
        if not existing_chat:
            try:
                # Получаем информацию о чате через Telegram API
                chat_info = bot.get_chat(chat_id)
                chat_name = chat_info.title  # Название чата
                if chat_name:
                    # Добавляем чат в таблицу chats
                    chat_manager.add_chat(chat_id=chat_id, chat_name=chat_name)
                    logging.info(f"""Чат {chat_id} с названием '{
                                 chat_name}' добавлен в таблицу chats.""")
            except Exception as e:
                logging.info(f"Не удалось добавить чат {chat_id}: {e}")
        else:
            if not existing_chat.chat_name:
                logging.info(f'''Удаляем чат с названием {
                             existing_chat.chat_name}''')
                chat_manager.delete_chat(chat_id)
            logging.info(f"Чат {chat_id} уже существует в базе данных.")


def update_usernames(bot):
    """
    Обновляет поле username в таблице users, если оно изменилось,
    используя Telegram API для получения имени и фамилии пользователей.
    """
    from app.database.managers.user_manager import UserManager

    # Менеджер пользователей
    db = UserManager()
    users = db.get_users()

    for user in users:
        try:
            # Получаем информацию о пользователе через Telegram API
            user_info = bot.get_chat(user.user_id)
            username = f"{user_info.first_name}"
            if user_info.last_name:
                username += f" {user_info.last_name}"
        except Exception as e:
            logging.warning(f"""Не удалось обновить пользователя {
                            user.user_id}: {e}""")
