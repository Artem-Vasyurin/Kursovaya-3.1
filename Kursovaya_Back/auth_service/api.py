# auth_service/api.py
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from auth_service.database import get_db
from auth_service.models import User
from auth_service.tokens import create_access_token
from auth_service.auth import verify_password, hash_password

router = APIRouter()

class RegisterUser(BaseModel):
    username: str
    password: str
    email: EmailStr

class LoginUser(BaseModel):
    username: str
    password: str

@router.post("/register", status_code=201)
async def register_user(user: RegisterUser, db: Session = Depends(get_db)):
    if db.query(User).filter((User.username == user.username) | (User.email == user.email)).first():
        raise HTTPException(status_code=400, detail="User with this username or email already exists")
    hashed_password = hash_password(user.password)
    new_user = User(username=user.username, password=hashed_password, email=user.email)
    db.add(new_user)
    db.commit()
    return {"message": "User registered successfully"}

@router.post("/login")
async def login_user(user: LoginUser, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == user.username).first()
    if not db_user or not verify_password(user.password, db_user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}
