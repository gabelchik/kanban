#!/bin/sh
set -e

echo "Применяем миграции.."
python manage.py migrate --noinput

exec "$@"