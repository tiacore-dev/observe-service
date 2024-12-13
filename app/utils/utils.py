from datetime import datetime, time

def parse_time(time_str):
    """
    Парсит строку времени в объект time, поддерживая форматы с и без секунд.
    """
    if isinstance(time_str, datetime.time):
        return time_str  # Если это уже объект time, возвращаем его

    for fmt in ('%H:%M', '%H:%M:%S'):
        try:
            return datetime.strptime(time_str, fmt).time()
        except ValueError:
            continue
    raise ValueError(f"Некорректный формат времени: {time_str}")