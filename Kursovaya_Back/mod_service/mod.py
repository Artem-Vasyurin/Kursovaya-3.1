from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from .models import Modification, Category
from auth_service.models import User
from auth_service import database as database_users
from sqlalchemy import text
import os
from fastapi import HTTPException, UploadFile
from datetime import datetime
import shutil

import pika
import json
import os


UPLOAD_DIRECTORY = "./uploaded_mods/"  # Папка для сохранения файлов

def save_mod_file(file: UploadFile):
    """Сохранение файла на сервере"""
    file_location = os.path.join(UPLOAD_DIRECTORY, file.filename)
    with open(file_location, "wb") as f:
        shutil.copyfileobj(file.file, f)
    return file_location

def create_modification(db: Session, name: str, description: str, category_id: int, author_id: int, file: UploadFile = None):
    # Проверяем, существует ли категория
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=400, detail="Category not found")

    # Проверяем, существует ли автор
    user_exists = database_users.query(User).filter(User.id == author_id).first()
    if not user_exists:
        raise HTTPException(status_code=400, detail="Author not found")

    # Сохраняем файл, если он был загружен
    file_path = None
    if file:
        file_path = save_mod_file(file)

    # Создаем модификацию
    new_mod = Modification(
        name=name,
        description=description,
        category_id=category_id,
        author_id=author_id,  # Добавляем автора
        file_path=file_path,
        created_at=int(datetime.now().timestamp()),
        updated_at=int(datetime.now().timestamp())
    )
    db.add(new_mod)
    db.commit()
    db.refresh(new_mod)

    # Отправка сообщения в RabbitMQ
    send_mod_message({"event": "mod_created", "mod_id": new_mod.id, "author_id": author_id})

    return new_mod


def delete_modification(db: Session, mod_id: int):
    # Проверяем, существует ли модификация
    mod = db.query(Modification).filter(Modification.id == mod_id).first()
    if not mod:
        raise HTTPException(status_code=404, detail="Modification not found")

    # Удаляем файл мода
    if mod.file_path and os.path.exists(mod.file_path):
        os.remove(mod.file_path)

    # Удаляем модификацию из базы данных
    db.delete(mod)
    db.commit()

    # Отправка сообщения в RabbitMQ
    send_mod_message({"event": "mod_deleted", "mod_id": mod_id})

    return {"message": "Modification deleted successfully"}



def get_modifications(db: Session, skip: int = 0, limit: int = 100):
    try:
        return db.query(Modification).offset(skip).limit(limit).all()
    except SQLAlchemyError as e:
        db.rollback()  # Откатываем изменения в случае ошибки
        raise Exception(f"Ошибка при получении модификаций: {str(e)}")

def create_category(db: Session, name: str):
    try:
        db_category = Category(name=name)
        db.add(db_category)
        db.commit()
        db.refresh(db_category)
        return db_category
    except SQLAlchemyError as e:
        db.rollback()  # Откатываем изменения в случае ошибки
        raise Exception(f"Ошибка при создании категории: {str(e)}")

def delete_category(db: Session, category_id: int):
    # Проверяем, существует ли категория
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    # Проверяем, есть ли моды в категории
    mods = db.query(Modification).filter(Modification.category_id == category_id).all()
    if mods:
        raise HTTPException(status_code=400, detail="Category is not empty")

    # Удаляем категорию из базы данных
    db.delete(category)
    db.commit()

    return {"message": "Category deleted successfully"}

def get_categories(db: Session, skip: int = 0, limit: int = 100):
    try:
        return db.query(Category).offset(skip).limit(limit).all()
    except SQLAlchemyError as e:
        db.rollback()  # Откатываем изменения в случае ошибки
        raise Exception(f"Ошибка при получении категорий: {str(e)}")

RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost")
RABBITMQ_PORT = os.getenv("RABBITMQ_PORT", 5672)

def send_mod_message(mod_data):
    connection = pika.BlockingConnection(pika.ConnectionParameters(RABBITMQ_HOST, RABBITMQ_PORT))
    channel = connection.channel()

    # Отправка в очередь mod_queue
    message = json.dumps(mod_data)
    channel.basic_publish(
        exchange='',
        routing_key='mod_queue',
        body=message,
        properties=pika.BasicProperties(
            delivery_mode=2,  # Сообщение будет сохраняться в случае сбоя
        )
    )
    print(f"Sent mod data to RabbitMQ: {mod_data}")
    connection.close()
