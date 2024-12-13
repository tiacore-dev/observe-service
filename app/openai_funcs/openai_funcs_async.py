import logging
import json
from openai import AsyncOpenAI


async def chatgpt_analyze_async(prompt, messages):
    """
    Запускает анализ набора сообщений через OpenAI API с возможностью отправки изображений.

    :param prompt: Текст системного промпта.
    :param messages: Список сообщений (JSON), включая ссылки на изображения.
    :return: Результат анализа и количество использованных токенов.
    """
    logging.info(f"Начало анализа набора сообщений.")

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
    

    logging.info("Начало проведения анализа")

    messages = [{"role": "system", "content": prompt}, {"role": "user", "content": f"{api_messages}"}]
    try:
        # Вызов OpenAI API
        response = await AsyncOpenAI.chat.completions.create(
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
