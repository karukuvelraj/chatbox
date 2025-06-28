from app.celery import celery_app
from app.services.message import update_is_delivered

@celery_app.task
def update_message_status():    
    print(f"Updating online users' message delivery status...")
    update_is_delivered()
    print(f"Online users' message delivery status updated successfully.")

