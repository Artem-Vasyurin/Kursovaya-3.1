import json
import pika
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from datetime import datetime
from auth_service.database import get_db
from auth_service.models import User
from auth_service.tokens import create_access_token
from auth_service.auth import verify_password, hash_password
from auth_service.rabbitmq import create_rabbitmq_channel
from auth_service.config import RABBITMQ_QUEUE

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

    # Отправка данных в RabbitMQ
    channel = create_rabbitmq_channel()
    message = {
        "event": "user_registered",
        "username": user.username,
        "timestamp": datetime.utcnow().isoformat()
    }
    channel.basic_publish(
        exchange='',
        routing_key=RABBITMQ_QUEUE,
        body=json.dumps(message)
    )

    return {"message": "User registered successfully"}

@router.delete("/delete/{username}", status_code=200)
async def delete_user(username: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user)
    db.commit()

    # Отправка данных об удалении в RabbitMQ
    channel = create_rabbitmq_channel()
    message = {
        "event": "user_deleted",
        "username": username,
        "timestamp": datetime.utcnow().isoformat()
    }
    channel.basic_publish(
        exchange='',
        routing_key=RABBITMQ_QUEUE,
        body=json.dumps(message)
    )

    return {"message": f"User {username} deleted successfully"}

@router.post("/login")
async def login_user(user: LoginUser, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == user.username).first()
    if not db_user or not verify_password(user.password, db_user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    access_token = create_access_token(data={"sub": user.username})

    # Отправляем информацию о входе в RabbitMQ
    try:
        channel = create_rabbitmq_channel()
        message = {
            "event": "user_logged_in",
            "username": user.username,
            "timestamp": datetime.utcnow().isoformat()
        }
        channel.basic_publish(
            exchange='',
            routing_key=RABBITMQ_QUEUE,
            body=json.dumps(message),
            properties=pika.BasicProperties(
                delivery_mode=2  # Сообщение будет сохраняться
            )
        )
        print(f"Информация о входе пользователя {user.username} отправлена в RabbitMQ.")
    except Exception as e:
        print(f"Ошибка при отправке информации о входе пользователя в RabbitMQ: {e}")

    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/users")
async def get_all_users(db: Session = Depends(get_db)):
    # Получаем всех пользователей из базы данных
    users = db.query(User).all()
    user_list = [{"id": user.id, "username": user.username, "email": user.email} for user in users]

    # Отправляем событие в RabbitMQ
    try:
        channel = create_rabbitmq_channel()
        message = {
            "event": "get_all_users_called",
            "timestamp": datetime.utcnow().isoformat(),
            "user_count": len(users)
        }
        channel.basic_publish(
            exchange='',
            routing_key=RABBITMQ_QUEUE,
            body=json.dumps(message),
            properties=pika.BasicProperties(
                delivery_mode=2  # Сообщение будет сохраняться
            )
        )
        print("Информация о вызове контроллера получения всех пользователей отправлена в RabbitMQ.")
    except Exception as e:
        print(f"Ошибка при отправке информации в RabbitMQ: {e}")

    return {"users": user_list}
