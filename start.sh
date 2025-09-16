celery -A SmartVillage worker --loglevel=info --concurrency=1 &

gunicorn SmartVillage.wsgi:application --bind 0.0.0.0:${PORT:-10000}
