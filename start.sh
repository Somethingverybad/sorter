#!/bin/bash

# Создание необходимых директорий
mkdir -p /app/staticfiles
mkdir -p /app/media

# Применение миграций
echo "Применение миграций..."
python manage.py migrate --noinput

# Создание отсутствующих миграций (если нужно)
echo "Проверка миграций..."
python manage.py makemigrations --noinput

# Повторное применение миграций после создания новых
echo "Применение новых миграций..."
python manage.py migrate --noinput

# Сбор статических файлов (без --clear чтобы избежать ошибки очистки)
echo "Сбор статических файлов..."
python manage.py collectstatic --noinput

# Альтернатива: принудительно устанавливаем права и владельца
chmod -R 755 /app/staticfiles
chown -R www-data:www-data /app/staticfiles || true

# Проверка статических файлов
echo "Проверка статических файлов..."
ls -la /app/staticfiles/ | head -10

# Запуск Gunicorn
echo "Запуск Gunicorn..."
gunicorn --bind 0.0.0.0:8000 --workers 3 botdiwatch.wsgi:application &

# Запуск Nginx
echo "Запуск Nginx..."
nginx -g "daemon off;"