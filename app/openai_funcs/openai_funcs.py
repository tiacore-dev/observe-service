import openai
from io import BytesIO
import logging





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

        response = openai.Audio.transcriptions.create(
            model="whisper-1",
            file=audio_file,
            language="ru"
        )
        return response.text
    except Exception as e:
        logging.error(f"Ошибка при вызове OpenAI API: {e}")
    finally:
        audio_file.close()


def chatgpt_analyze(prompt, messages):
    """
    Запускает анализ набора сообщений через OpenAI API.

    :param prompt: Текст системного промпта.
    :param messages: Список сообщений (JSON).
    :return: Результат анализа и количество использованных токенов.
    """
    logging.info(f"Начало анализа набора сообщений.")

    # Форматируем сообщения для OpenAI API
    api_messages = [{"role": "system", "content": prompt}]
    for msg in messages:
        if "text" in msg and msg["text"]:  # Учитываем только сообщения с текстом
            formatted_message = (
                f"Пользователь: {msg['user_id']}, "
                f"Чат: {msg['chat_id']}, "
                f"Дата: {msg['timestamp']}, "
                f"Сообщение: {msg['text']}"
            )
            api_messages.append({"role": "user", "content": formatted_message})

    try:
        # Вызов OpenAI API
        response = openai.chat.completions.create(
            model="gpt-4",  # Убедитесь, что это правильная модель
            messages=api_messages
        )

        # Получение результата анализа
        analysis = response.choices[0].message.content
        tokens = response.usage.total_tokens

        logging.info("Анализ текста завершен.", extra={'user_id': 'openai'})
        return analysis, tokens

    except Exception as e:
        logging.error(f"Ошибка OpenAI API: {e}")
        raise e
