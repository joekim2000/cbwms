from __future__ import absolute_import

import os

from celery import Celery
from celery.schedules import crontab

from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cbwms.settings.development')
import django
django.setup()

#app = Celery('cbwms',       # 현재 프로젝트의 이름
#            broker='redis://localhost:6379')  # broker: 브로커에 접속할 수 있는 URL을 설정.
app = Celery()

app.config_from_object('django.conf:settings')
app.conf.timezone = 'Asia/Seoul'
app.conf.enable_utc = True
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)
app.conf.update(
    BROKER_URL='redis://localhost:6379',
    CELERY_RESULT_BACKEND = 'redis://localhost:6379',
)

@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    #sender.add_periodic_task(crontab(minute='*/5'), personnel, name='update every 5 minutes in a day')
    sender.add_periodic_task(crontab(hour=16, minute=15), personnel, name='run every day')
    #sender.add_periodic_task(crontab(hour=19, minute=49, day_of_week=1), test.s('Happy Mondays!'), name='add every 60 seconds')
    #sender.add_periodic_task(60, personnel, name='add every 60 seconds')
    return

@app.task
def personnel():
    from apps.caengine.tasks import checkaccounts
    checkaccounts()
