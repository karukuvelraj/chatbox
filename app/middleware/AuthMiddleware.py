from fastapi import HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from jose import JWTError, jwt
from app.config import settings
from app.models.user import User
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.utils.auth import decode_access_token


SECRET_KEY = settings.secret_key
ALGORITHM = settings.algorithm

class JWTMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.scope.get("type") == "websocket":
            response = await call_next(request)
            return response
        
        token = request.headers.get("Authorization")
        
        if token:
            token = token.split(" ")[1] 
            
            try:
                payload = decode_access_token(token)
                user_id = payload.get("sub")
                
                if user_id is None:
                    return JSONResponse(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        content={'detail': "Invalid token"},
                        headers={"WWW-Authenticate": "Bearer"}
                    )
                
                db: Session = next(get_db())
                user = db.query(User).filter(User.id == user_id).first()
                
                if user is None:
                    return JSONResponse(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        content={'detail': "User not found"},
                        headers={"WWW-Authenticate": "Bearer"}
                    )
            
            except JWTError as e:
                if 'exp' in str(e):
                    return JSONResponse(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        content={'detail': "Token has expired"},
                        headers={"WWW-Authenticate": "Bearer"}
                    )
                else:
                    return JSONResponse(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        content={'detail': "Could not validate credentials"},
                        headers={"WWW-Authenticate": "Bearer"}
                    )
                    
            except Exception as e:
                error = str(e)
                status_str, detail = error.split(":", 1)
                status_code = int(status_str.strip())
                detail = detail.strip()
                return JSONResponse(
                    status_code=status_code,
                    content={'detail':detail},
                    headers={"WWW-Authenticate": "Bearer"}
                )

        response = await call_next(request)
        return response

