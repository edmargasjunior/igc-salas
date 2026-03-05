"""Celery config para IGC Salas."""
import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'igc_salas.settings.production')
app = Celery('igc_salas')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
