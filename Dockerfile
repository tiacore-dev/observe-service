# Используем официальный образ Python в качестве базового
FROM python:3.12-slim

# Устанавливаем необходимые зависимости, включая ffmpeg, curl, gcc и библиотеки для SSL
RUN apt-get update && apt-get install -y \
    curl \
    ffmpeg \
    gcc \
    libpq-dev \
    libssl-dev \
    libcurl4-openssl-dev \
    dnsutils \
    && rm -rf /var/lib/apt/lists/*

RUN apt-get update && apt-get install -y \
    ca-certificates \
    && update-ca-certificates


# Указываем рабочую директорию внутри контейнера
WORKDIR /app

# Копируем файл зависимостей в рабочую директорию
COPY requirements.txt .

# Обновляем pip до последней версии
RUN python -m pip install --upgrade pip

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Устанавливаем Gunicorn
RUN pip install gunicorn


# Копируем весь код приложения в рабочую директорию
COPY . .


