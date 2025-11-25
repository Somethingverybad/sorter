FROM python:3.12-slim

# Установка зависимостей системы
RUN apt-get update && apt-get install -y \
    nginx \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Создание директорий
RUN mkdir -p /app/static /app/media /app/logs

# Установка Python зависимостей
COPY requirements.txt /app/
WORKDIR /app
RUN pip install --no-cache-dir -r requirements.txt

# Копирование проекта
COPY . /app/

# Копирование конфигурации nginx
COPY nginx.conf /etc/nginx/sites-available/default

# Создание скрипта для запуска
COPY start.sh /app/
RUN chmod +x /app/start.sh

# Открытие портов
EXPOSE 8000 80

# Запуск приложения
CMD ["/app/start.sh"]   