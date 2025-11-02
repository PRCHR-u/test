#!/bin/sh
# entrypoint.sh - Стартовый скрипт для веб-контейнера

# Применяем миграции базы данных
echo "Applying database migrations..."
python manage.py migrate
