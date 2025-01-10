import logging
import json
from io import BytesIO
import backoff
import openai
from app.utils.db_get import get_chat_name, get_user_name


# Класс NamedBytesIO с именем
class NamedBytesIO(BytesIO):
    def __init__(self, initial_bytes, name):
        super().__init__(initial_bytes)
        self.name = name


# Транскрибация аудио
def transcribe_audio(audio, file_format):
    audio_file = NamedBytesIO(audio, f"audio.{file_format}")
    audio_file.seek(0)
    try:
        logging.info("Параметры вызова OpenAI API:")
        logging.info({
            "model": "whisper-1",
            "file": audio_file,
            "language": "ru"
        })

        response = openai.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file,
            language="ru"
        )
        return response.text
    except Exception as e:
        logging.error(f"Ошибка при вызове OpenAI API: {e}")
    finally:
        audio_file.close()


@backoff.on_exception(
    backoff.expo,
    (openai.OpenAIError, ConnectionError),  # Исправленный импорт
    max_tries=5,
    max_time=30  # Максимальное время ожидания
)
def chatgpt_analyze(prompt, messages):
    """
    Запускает анализ набора сообщений через OpenAI API с возможностью отправки изображений.

    :param prompt: Текст системного промпта.
    :param messages: Список сообщений (JSON), включая ссылки на изображения.
    :return: Результат анализа и количество использованных токенов.
    """
    logging.info("Начало анализа набора сообщений.")

    api_messages = []

    for msg in messages:
        # Учитываем только сообщения с текстом
        if "text" in msg and msg["text"]:

            user = get_user_name(msg.get("user_id"))
            chat = get_chat_name(msg.get("chat_id"))

            message_data = {
                "user": user,
                "chat": chat,
                "timestamp": msg.get("timestamp", "Неизвестно"),
                "text": msg.get("text", "Пустое сообщение"),
            }
            # Добавляем сообщение как JSON
            api_messages.append(
                json.dumps(message_data, ensure_ascii=False)
            )

    logging.info("Начало проведения анализа")
    messages = [{"role": "system", "content": prompt},
                {"role": "user", "content": f"{api_messages}"}]
    try:
        # Вызов OpenAI API
        response = openai.chat.completions.create(
            model="gpt-4o",  # Убедитесь, что используете правильную модель
            messages=messages
        )
        # Получение результата анализа
        analysis = response.choices[0].message.content
        tokens_input = response.usage.prompt_tokens  # Токены на отправку
        tokens_output = response.usage.completion_tokens  # Токены на ответ

        logging.info("Анализ текста завершен.")
        return analysis, tokens_input, tokens_output

    except Exception as e:
        logging.error(f"Ошибка OpenAI API: {e}")
        raise e
