from fastapi import FastAPI
from app.middleware.AuthMiddleware import JWTMiddleware
from app.api import user, message, websocket

app = FastAPI()

app.add_middleware(JWTMiddleware)

app.include_router(user.router, prefix="/user", tags=["users"])
app.include_router(message.router, prefix="/messages", tags=["messages"])
app.include_router(websocket.router)


@app.get("/")
def read_root():
    return {"message": "Welcome to the chat application!"}

