from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate, UserResponse, UserLogin
from app.services.user import create_user, update_user, delete_user
from app.db.database import get_db
from app.utils import auth, hashing


router = APIRouter()

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = create_user(db=db, user=user)
    return db_user


@router.post("/login")
def login_user(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == user.username).first()
    if not db_user or not hashing.verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=400, detail="Invalid credentials")
    
    access_token = auth.create_access_token(data={"sub": db_user.id})
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/{user_id}", response_model=UserResponse, status_code=status.HTTP_200_OK)
def get_user(user_id: int, db: Session = Depends(get_db), current_user: User = Depends(auth.get_current_user)):
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@router.put("/update/{user_id}", response_model=UserResponse)
def user_update(user_id: int, user_update: UserUpdate, db: Session = Depends(get_db), current_user: User = Depends(auth.get_current_user)):
    return update_user(db=db, user_id=user_id, user_update=user_update)


@router.delete("/delete/{user_id}")
def user_delete(user_id: int, db: Session = Depends(get_db), current_user: User = Depends(auth.get_current_user)):
    return delete_user(db=db, user_id=user_id)
