import os
from celery import Celery
from config import Config

celery_app = Celery(
    "sidequest",
    broker=Config.REDIS_URL,
    backend=Config.REDIS_URL,
)

@celery_app.task
def example_task(x):
    return x * 2
