import logging
import json
from io import BytesIO
import tempfile
from pydub import AudioSegment
import requests
from app.utils.db_get import get_chat_name, get_user_name
from app.yandex_funcs.yandex_setup import YANDEX_API_KEY, YANDEX_GPT_API_URL, YANDEX_SPEECHKIT_API_URL, FOLDER_ID


# Функция конвертации аудио в LPCM (WAV) 16kHz
def convert_audio_to_lpcm(audio_bytes, file_format):
    try:
        audio = AudioSegment.from_file(
            BytesIO(audio_bytes), format=file_format)
        audio = audio.set_frame_rate(16000).set_channels(
            1).set_sample_width(2)  # 16-bit PCM

        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
        audio.export(temp_file.name, format="wav")  # Экспортируем в WAV
        temp_file.close()
        return temp_file.name
    except Exception as e:
        logging.error(f"Ошибка конвертации аудио: {e}")
        return None


# Функция транскрибации аудио через Yandex SpeechKit
def transcribe_audio(audio, file_format):
    audio_path = convert_audio_to_lpcm(audio, file_format)
    if not audio_path:
        return None

    headers = {
        "Authorization": f"Api-Key {YANDEX_API_KEY}"
    }

    params = {
        "folderId": FOLDER_ID,
        "lang": "ru-RU",
        "format": "lpcm",  # Указываем правильный формат
        "sampleRateHertz": 16000
    }

    try:
        logging.info("Отправка аудио в Yandex SpeechKit")

        with open(audio_path, "rb") as audio_file:
            response = requests.post(
                YANDEX_SPEECHKIT_API_URL,
                headers=headers,
                params=params,
                files={"file": audio_file},
                timeout=300
            )

        response_data = response.json()
        if "result" in response_data:
            return response_data["result"]
        else:
            logging.error(f"Ошибка транскрибации: {response_data}")
            return None
    except Exception as e:
        logging.error(f"Ошибка при вызове Yandex SpeechKit API: {e}")
        return None


# Функция анализа текста через YandexGPT
def chatgpt_analyze(prompt, messages):
    """
    Анализирует сообщения через YandexGPT.

    :param prompt: Текст системного промпта.
    :param messages: Список сообщений (JSON).
    :return: Результат анализа.
    """
    logging.info("Начало анализа набора сообщений.")

    api_messages = []

    for msg in messages:
        if "text" in msg and msg["text"]:
            user = get_user_name(msg.get("user_id"))
            chat = get_chat_name(msg.get("chat_id"))

            message_data = {
                "user": user,
                "chat": chat,
                "timestamp": msg.get("timestamp", "Неизвестно"),
                "text": msg.get("text", "Пустое сообщение"),
            }
            api_messages.append(json.dumps(message_data, ensure_ascii=False))

    headers = {
        "Authorization": f"Api-Key {YANDEX_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "modelUri": f"gpt://{FOLDER_ID}/yandexgpt-lite",
        "completionOptions": {
            "stream": False,
            "temperature": 0.6,
            "maxTokens": 2000
        },
        "messages": [
            {"role": "system", "text": prompt},
            {"role": "user", "text": f"{api_messages}"}
        ]
    }

    try:
        response = requests.post(
            YANDEX_GPT_API_URL,
            headers=headers,
            json=payload,
            timeout=300
        )
        response_data = response.json()

        if "result" in response_data:
            analysis = response_data["result"]["alternatives"][0]["message"]["text"]
            return analysis, None, None  # В YandexGPT пока нет токенов
        else:
            logging.error(f"Ошибка анализа: {response_data}")
            return None, None, None
    except Exception as e:
        logging.error(f"Ошибка при вызове YandexGPT API: {e}")
        return None, None, None
