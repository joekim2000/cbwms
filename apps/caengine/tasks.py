from __future__ import absolute_import

from cbwms.settings.celery import app
#from celery.schedules import crontab

from django.conf import settings
PROJECT_ROOT = getattr(settings, "PROJECT_ROOT", None)
APPS_ROOT = PROJECT_ROOT + "/apps/caengine/bin"
import sys
sys.path.append(APPS_ROOT)
import caengineimport
import subprocess

@app.task()
def checkaccounts():
    caengineimport.Run()
