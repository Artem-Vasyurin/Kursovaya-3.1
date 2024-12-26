from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.orm import Session
from . import models, database, mod
from auth_service.models import User
from fastapi import HTTPException
from auth_service import database as database_users


router = APIRouter()

@router.post("/modifications/")
def create_modification(
    name: str,
    description: str,
    category_id: int,
    author_id: int,  # Указание автора
    file: UploadFile = File(None),
    db: Session = Depends(database.get_db)
):
    # Проверяем, существует ли автор
    user_exists = database_users .query(User).filter(User.id == author_id).first()
    if not user_exists:
        raise HTTPException(status_code=400, detail="Author not found")

    return mod.create_modification(db, name, description, category_id, author_id, file)

@router.post("/modifications/")
def create_modification(
    name: str,
    description: str,
    category_id: int,
    author_id: int,  # Указание автора
    file: UploadFile = File(None),
    db: Session = Depends(database.get_db)
):
    return mod.create_modification(db, name, description, category_id, author_id, file)

@router.delete("/modifications/{mod_id}")
def delete_modification(mod_id: int, db: Session = Depends(database.get_db)):
    return mod.delete_modification(db, mod_id)

@router.post("/categories/")
def create_category(name: str, db: Session = Depends(database.get_db)):
    return mod.create_category(db, name)

@router.delete("/categories/{category_id}")
def delete_category(category_id: int, db: Session = Depends(database.get_db)):
    return mod.delete_category(db, category_id)

@router.get("/categories/")
def read_categories(skip: int = 0, limit: int = 100, db: Session = Depends(database.get_db)):
    categories = mod.get_categories(db, skip=skip, limit=limit)
    return categories
