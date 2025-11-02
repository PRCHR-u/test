#!/bin/sh
# entrypoint.sh - Стартовый скрипт для веб-контейнера

# Применяем миграции базы данных
echo "Applying database migrations..."
python manage.py migrate

# Запускаем команду, переданную в Docker CMD.
# `exec "$@"` заменяет текущий процесс на новый,
# что является лучшей практикой для Docker-контейнеров.
exec "$@"
