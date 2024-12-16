import logging
import json
from openai import AsyncOpenAI

client = AsyncOpenAI()

async def chatgpt_analyze_async(prompt, messages):
    """
    Запускает анализ набора сообщений через OpenAI API.
    """
    logging.info(f"Начало анализа набора сообщений.")

    api_messages = []
    for msg in messages:
        if "text" in msg and msg["text"]:  # Учитываем только сообщения с текстом
            message_data = {
                "user_id": msg.get("user_id", "Неизвестно"),
                "chat_id": msg.get("chat_id", "Неизвестно"),
                "timestamp": str(msg.get("timestamp", "Неизвестно")),  # Убедитесь, что timestamp строка
                "text": msg.get("text", "Пустое сообщение"),
            }
            api_messages.append(json.dumps(message_data, ensure_ascii=False))

    logging.info("Начало проведения анализа")

    # Формируем правильный запрос
    try:
        messages_payload = [{"role": "system", "content": prompt}]
        for msg in api_messages:
            messages_payload.append({"role": "user", "content": msg})

        # Вызов OpenAI API
        response = await client.chat.completions.create(
            model="gpt-4",  # Убедитесь, что используете правильную модель
            messages=messages_payload
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
