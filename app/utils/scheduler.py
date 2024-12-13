from datetime import datetime, timedelta
import logging
import asyncio
from app.utils.bot_utils import send_analysis_with_chat_link
from app.openai_funcs.openai_funcs_async import chatgpt_analyze_async

from apscheduler.schedulers.background import BackgroundScheduler

scheduler = BackgroundScheduler()

async def execute_analysis_and_send(chat_id, analysis_time):
    """
    Выполняет анализ сообщений для указанного чата и отправляет результат в Telegram.
    """
    from app.database.managers.message_manager import MessageManager
    from app.database.managers.chat_manager import ChatManager
    from app.openai_funcs.openai_funcs_async import chatgpt_analyze_async
    from app.utils.bot_utils import send_analysis_with_chat_link

    chat_manager = ChatManager()
    message_manager = MessageManager()

    try:
        chat = chat_manager.get_chat_by_id(chat_id)
        if not chat:
            logging.warning(f"Чат {chat_id} не найден.")
            return

        # Формируем диапазон времени для анализа
        now = datetime.utcnow()
        analysis_start = datetime.combine(now.date() - timedelta(days=1), analysis_time)
        analysis_end = datetime.combine(now.date(), analysis_time)

        messages = message_manager.get_filtered_messages(
            start_date=analysis_start,
            end_date=analysis_end,
            chat_id=chat_id
        )

        if not messages:
            logging.warning(f"Нет сообщений для анализа в чате {chat_id}.")
            return

        # Выполнение анализа
        prompt = chat.default_prompt or "Системный промпт для анализа."
        analysis_result, tokens_input, tokens_output = await chatgpt_analyze_async(prompt, messages)

        # Формирование текста результата
        result_text = f"Результат анализа:\n{analysis_result}\n\n"
        result_text += f"Токены ввода: {tokens_input}, Токены вывода: {tokens_output}"

        """# Отправка результата в Telegram
        await send_analysis_with_chat_link(
            bot_token="ваш_токен_бота",
            target_chat_id=-1001234567890,  # Ваш целевой чат
            analysis_text=result_text,
            chat_username=f"chat_{chat_id}"
        )"""

        logging.info(f"Анализ для чата {chat_id} успешно выполнен и отправлен.")
    except Exception as e:
        logging.error(f"Ошибка при выполнении анализа для чата {chat_id}: {e}")



def start_scheduler():
    """
    Запуск планировщика с асинхронной обработкой и загрузкой задач из базы.
    """
    
    from app.database.managers.chat_manager import ChatManager

    

    # Инициализация задач из базы данных
    chat_manager = ChatManager()
    try:
        chats = chat_manager.get_all_chats()
        for chat in chats:
            if chat.schedule_analysis and chat.send_time:
                # Добавляем задачу для каждого чата с активным расписанием
                add_schedule_to_scheduler(
                    scheduler=scheduler,
                    chat_id=chat.chat_id,
                    analysis_time=chat.analysis_time,
                    send_time=chat.send_time
                )
        logging.info("Все задачи из базы данных добавлены в планировщик.")
    except Exception as e:
        logging.error(f"Ошибка при инициализации планировщика из базы данных: {e}")

    scheduler.start()
    logging.info("Планировщик успешно запущен.")



def add_schedule_to_scheduler(chat_id, analysis_time, send_time):
    """
    Добавляет или обновляет задачу анализа для указанного чата.
    """
    if not analysis_time or not send_time:
        logging.warning(f"Невозможно добавить задачу для чата {chat_id}: время анализа или отправки не указано.")
        return

    scheduler.add_job(
        execute_analysis_and_send,  # Единая функция анализа и отправки
        'cron',
        hour=send_time.hour,
        minute=send_time.minute,
        args=[chat_id, analysis_time],
        id=f"schedule_{chat_id}"
    )
    logging.info(f"Задача для чата {chat_id} добавлена в планировщик: анализ в {analysis_time}, отправка в {send_time}.")


def remove_schedule_from_scheduler(chat_id):
    """
    Удаляет задачу из планировщика по ID чата.
    """
    try:
        scheduler.remove_job(f"schedule_{chat_id}")
        logging.info(f"Задача для чата {chat_id} удалена из планировщика.")
    except Exception as e:
        logging.warning(f"Ошибка при удалении задачи для чата {chat_id}: {e}")
