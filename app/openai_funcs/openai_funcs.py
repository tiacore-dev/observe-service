import openai
from io import BytesIO
import logging
import json




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


def chatgpt_analyze(prompt, messages):
    """
    Запускает анализ набора сообщений через OpenAI API с возможностью отправки изображений.

    :param prompt: Текст системного промпта.
    :param messages: Список сообщений (JSON), включая ссылки на изображения.
    :return: Результат анализа и количество использованных токенов.
    """
    logging.info(f"Начало анализа набора сообщений.")

    #from app.s3 import get_s3_manager, get_bucket_name
    #s3_manager = get_s3_manager()
    #bucket_name = get_bucket_name()
    #files = []  # Список файлов для отправки в OpenAI
    api_messages = []
    for msg in messages:
        if "text" in msg and msg["text"]:  # Учитываем только сообщения с текстом
                message_data = {
                    "user_id": msg.get("user_id", "Неизвестно"),
                    "chat_id": msg.get("chat_id", "Неизвестно"),
                    "timestamp": msg.get("timestamp", "Неизвестно"),
                    "text": msg.get("text", "Пустое сообщение"),
                }
                # Добавляем сообщение как JSON
                api_messages.append(
                    json.dumps(message_data, ensure_ascii=False)
                )
    
        """# Проверяем наличие s3_key и скачиваем файл
        if "s3_key" in msg and msg["s3_key"]:
            try:
                file_url = s3_manager.generate_presigned_url(bucket_name, msg['s3_key'])
                api_messages.append({
                    "role": "user",
                    "content": f"Файл доступен по ссылке: {file_url}",
                })
                #logging.info(f"Скачивание изображения из S3: {msg['s3_key']}")
                #file_content = s3_manager.get_file(bucket_name, msg['s3_key'])
                #files.append(("file", (msg["s3_key"], file_content, "application/octet-stream")))
            except Exception as e:
                logging.warning(f"Не удалось скачать файл {msg['s3_key']}: {e}")"""

    logging.info("Начало проведения анализа")

    messages = [{"role": "system", "content": prompt}, {"role": "user", "content": f"{api_messages}"}]
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
