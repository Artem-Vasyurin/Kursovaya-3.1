from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from .models import Modification, Category

from .rabbitmq import send_mod_message
import os
from fastapi import HTTPException, UploadFile
from datetime import datetime
import shutil

import pika
import json



UPLOAD_DIRECTORY = "./uploaded_mods/"  # Папка для сохранения файлов

def save_mod_file(file: UploadFile):
    """Сохранение файла на сервере"""
    file_location = os.path.join(UPLOAD_DIRECTORY, file.filename)
    with open(file_location, "wb") as f:
        shutil.copyfileobj(file.file, f)
    return file_location

def create_modification(db: Session, name: str, description: str, category_id: int, file: UploadFile = None):
    # Проверяем, существует ли категория
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=400, detail="Category not found")

    # Сохраняем файл, если он был загружен
    file_path = None
    if file:
        file_path = save_mod_file(file)

    # Создаем модификацию, если категория найдена
    new_mod = Modification(
        name=name,
        description=description,
        category_id=category_id,
        file_path=file_path,
        created_at=int(datetime.now().timestamp()),
        updated_at=int(datetime.now().timestamp())
    )
    db.add(new_mod)
    db.commit()
    db.refresh(new_mod)
    send_mod_message({"action": "create","name":new_mod.name,  "mod_data": new_mod.id})
    return new_mod

def delete_modification(db: Session, name: str):
    mod = db.query(Modification).filter(Modification.name == name).first()
    if not mod:
        raise HTTPException(status_code=404, detail="Modification not found")

    try:
        # Удаляем файл модификации
        if mod.file_path and os.path.exists(mod.file_path):
            os.remove(mod.file_path)

        db.delete(mod)
        db.commit()

        # Отправка сообщения в RabbitMQ об удалении
        send_mod_message({"action": "delete", "name":name, "mod_id": mod.id})

        return {"message": "Modification deleted successfully"}
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Error deleting modification")

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
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    try:
        db.delete(category)
        db.commit()

        # Отправка сообщения в RabbitMQ об удалении категории
        send_mod_message({"action": "delete", "category_data": category.id})

        return {"message": "Category deleted successfully"}
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Error deleting category")

def get_categories(db: Session, skip: int = 0, limit: int = 100):
    try:
        return db.query(Category).offset(skip).limit(limit).all()
    except SQLAlchemyError as e:
        db.rollback()  # Откатываем изменения в случае ошибки
        raise Exception(f"Ошибка при получении категорий: {str(e)}")

