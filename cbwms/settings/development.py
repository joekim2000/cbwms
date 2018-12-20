# Python imports
from os.path import join

# project imports
from .common import *

from celery.schedules import crontab

# uncomment the following line to include i18n
# from .i18n import *


# ##### DEBUG CONFIGURATION ###############################
DEBUG = True

# allow all hosts during development
ALLOWED_HOSTS = ['10.211.55.78', 'localhost', '127.0.0.1']

# adjust the minimal login
LOGIN_URL = 'core_login'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = 'core_login'


# ##### DATABASE CONFIGURATION ############################
#BROKER_URL='redis://localhost:6379',
#RESULT_BACKEND = 'mysql://secuadmin:secuqhdks87!@localhost/CBWMSDB',
#CELERY_TASK_SERIALIZER='json',
#CELERY_ACCEPT_CONTENT=['json'],  # Ignore other content
#CELERY_RESULT_SERIALIZER='json',
CELERY_TIMEZOME = 'Asia/Seoul'
#CELERY_TIMEZONE = 'UTC'
CELERY_ENABLE_UTC = True
CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers:DatabaseScheduler'
'''
CELERY_BEAT_SCHEDULER = {
    # Executes every Monday morning at 7:30 A.M
    "every-monday-morning": {
        "task": "tasks.add",
        "schedule": crontab(hour=14, minute=37, day_of_week=1),
        "args": (16, 16),
    },
}
'''
CACHES = {
	'default': {
		'BACKEND': 'django_redis.cache.RedisCache',
		'LOCATION': 'redis://127.0.0.1:6379/',
		'OPTIONS': {
			'init_command': 'ALTER DATABASE CBWMSDB CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci',
			'CLIENT_CLASS': 'django_redis.client.DefaultClient',
		}
	}	
}

DATABASES = {
	'default': {
		'OPTIONS': {
			'init_command': 'SET sql_mode=STRICT_TRANS_TABLES,storage_engine=INNODB',
		},
		'ENGINE': 'django.db.backends.mysql',
		'NAME': 'CBWMSDB',
		'USER': 'secuadmin',
		'PASSWORD': 'Secuqhdks87!',
		'HOST': 'localhost',
		'PORT': '',
		'CHARSET': 'utf8',
		'COLLATION': 'utf8_general_ci',
	}
}

LANGUAGE_CODE = 'ko-kr'
USE_TZ = True
TIME_ZONE = 'Asia/Seoul'

# ##### APPLICATION CONFIGURATION #########################

INSTALLED_APPS = DEFAULT_APPS
