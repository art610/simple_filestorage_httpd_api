# Берем легкий образ с Python 3.8
FROM python:3.8-alpine
# Выставляем переменные окружения
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
# Указываем рабочую директорию
WORKDIR /app
# Копируем все файлы из текущей директории в рабочую директорию контейнера
COPY . /app
# Обновляем и устанавливаем необходимые зависимости
RUN apk update && python -m pip install -r ./requirements.txt --no-cache-dir
# Указываем порт для слушания
EXPOSE 9090
# Запускаем приложение при старте контейнера
CMD python main.py
