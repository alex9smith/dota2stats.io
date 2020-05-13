from celery import Celery

CELERY_BROKER_URL = "redis://redis:6379"
CELERY_RESULT_BACKEND = "redis://redis:6379"

worker = Celery('tasks', broker=CELERY_BROKER_URL, backend=CELERY_RESULT_BACKEND)