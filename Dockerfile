# Используем официальный образ Python в качестве базового
FROM python:3.12-slim

# Указываем рабочую директорию внутри контейнера
WORKDIR /app

# Устанавливаем зависимости системы (включая curl)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN apt-get update && apt-get install -y \
    ca-certificates \
    && update-ca-certificates \
    && python3-distutils

# Копируем файл зависимостей в рабочую директорию
COPY requirements.txt .

# Устанавливаем Python-зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Устанавливаем Gunicorn
RUN pip install gunicorn

# Копируем сертификаты в контейнер (предполагается, что они находятся в папке certs на хосте)
COPY ./certs /app/certs

# Копируем весь код приложения в рабочую директорию
COPY . .

