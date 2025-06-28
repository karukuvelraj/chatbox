import json
import asyncio
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from app.models.user import User
from app.services.message import create_message, update_is_delivered
from app.utils import auth
from app.db.database import get_db
from app.websocket import ConnectionManager
import logging


logging.basicConfig(level=logging.DEBUG)

router = APIRouter()

manager = ConnectionManager()

@router.websocket("/chat/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: int, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    token = websocket.query_params.get('token')

    logging.debug(f"Incoming connection: user_id={user_id}, token={token}")
    
    if not token:
        logging.debug("Token is missing. Closing WebSocket.")
        await websocket.close(code=1000)
        return

    try:
        current_user = auth.get_current_user(token, db)
        logging.debug(f"User {current_user.id} authenticated successfully.")
    except HTTPException as e:
        logging.debug(f"HTTPException: {e}. Closing WebSocket.")
        await websocket.close(code=1000)
        return
    except Exception as e:
        logging.debug(f"Unexpected error: {e}. Closing WebSocket.")
        await websocket.close(code=1000)
        return

    if current_user.id != user_id:
        logging.debug(f"User ID mismatch. Expected {user_id}, but got {current_user.id}. Closing WebSocket.")
        await websocket.close(code=1000)
        return

    # Set the user as online
    current_user.is_online = True
    db.commit()
    
    await asyncio.to_thread(update_is_delivered, db, user_id)
    
    recipient_id = None
    
    await manager.connect(websocket, user_id)
    await websocket.send_text("Connection successful.")

    try:
        while True:
            data = await websocket.receive_text()
            logging.debug(f"Received data: {data}")

            try:
                message = json.loads(data)
                if 'recipient_id' in message:
                    recipient_id = message['recipient_id']
                    logging.debug(f"Recipient ID set: {recipient_id}")
                else:
                    if recipient_id:
                        if 'message' in message:
                            recipient = db.query(User).filter(User.id == recipient_id).first()
                            is_delivered = recipient.is_online if recipient else False

                            if recipient_id in manager.active_connections:
                                await manager.send_personal_message(f"{message['message']}", recipient_id)
                                await create_message(db, sender_id=user_id, receiver_id=recipient_id, content=message['message'], is_seen=False, is_delivered=is_delivered)
                            else:
                                await manager.send_personal_message(f"User {recipient_id} is not Online.", user_id)
                                await create_message(db, sender_id=user_id, receiver_id=recipient_id, content=message['message'], is_seen=False, is_delivered=False)
                    else:
                        await websocket.send_text("Recipient ID not provided.")
            except json.JSONDecodeError:
                await websocket.send_text("Invalid message format. Please use a valid JSON format.")
                continue
                
    except WebSocketDisconnect:
        logging.debug(f"WebSocket disconnected for user {user_id}.")
        manager.disconnect(user_id)
    finally:
        # Set the user as offline
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            user.is_online = False
            db.commit()
        