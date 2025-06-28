from fastapi import WebSocket

import logging

logging.basicConfig(level=logging.DEBUG)

class ConnectionManager:
    def __init__(self):
        self.active_connections = {}

    async def connect(self, websocket: WebSocket, user_id: int):
        await websocket.accept()
        self.active_connections[user_id] = websocket
        logging.debug(f"User {user_id} connected.")

    async def send_personal_message(self, message: str, user_id: int):
        websocket = self.active_connections.get(user_id)
        if websocket:
            await websocket.send_text(message)
        else:
            logging.debug(f"User {user_id} is not connected.")

    def disconnect(self, user_id: int):
        if user_id in self.active_connections:
            self.active_connections.pop(user_id)
            logging.debug(f"User {user_id} disconnected.")
