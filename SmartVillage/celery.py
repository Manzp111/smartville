# capstone_project/celery.py
import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "SmartVillage.settings")

app = Celery("SmartVillage")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()


app.conf.beat_schedule = {
    'cleanup-otps-every-5-minutes': {
        'task': 'account.tasks.cleanup_otps',
        'schedule': crontab(minute='*/5'),  # every 5 minutes
    },
}
