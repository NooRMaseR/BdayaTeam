import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'BdayaTeam.settings')

app = Celery('BdayaTeam')

app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()