from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from .models import Modification, Category
import os
from fastapi import HTTPException, UploadFile
from datetime import datetime
import shutil

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
    return new_mod

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

def get_categories(db: Session, skip: int = 0, limit: int = 100):
    try:
        return db.query(Category).offset(skip).limit(limit).all()
    except SQLAlchemyError as e:
        db.rollback()  # Откатываем изменения в случае ошибки
        raise Exception(f"Ошибка при получении категорий: {str(e)}")
