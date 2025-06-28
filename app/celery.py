from celery import Celery
from app.config import settings  


celery_app = Celery(
    "chatbox_app", 
    broker=f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/0",  
    backend=f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/0", 
)

celery_app.conf.update(
    result_expires=3600,
    task_track_started=True
)


