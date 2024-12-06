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

                # Добавляем чат в таблицу chats
                chat_manager.add_chat(chat_id=chat_id, chat_name=chat_name)
                logging.info(f"Чат {chat_id} с названием '{chat_name}' добавлен в таблицу chats.")
            except Exception as e:
                logging.info(f"Не удалось добавить чат {chat_id}: {e}")


