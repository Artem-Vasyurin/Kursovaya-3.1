from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.orm import Session
from . import models, database, mod
from fastapi import FastAPI, HTTPException, Request
from urllib.parse import unquote
import logging

router = APIRouter()

@router.post("/modifications/")
def create_modification(
    name: str,
    description: str,
    category_id: int,
    file: UploadFile = File(None),
    db: Session = Depends(database.get_db)
):
    return mod.create_modification(db, name, description, category_id, file)

@router.get("/modifications/")
def read_modifications(skip: int = 0, limit: int = 100, db: Session = Depends(database.get_db)):
    modifications = mod.get_modifications(db, skip=skip, limit=limit)
    return modifications

@router.delete("/modifications/{name}/")
def delete_modification(name: str, db: Session = Depends(database.get_db)):
    return mod.delete_modification(db, name)

@router.post("/categories/")
def create_category(name: str, db: Session = Depends(database.get_db)):
    return mod.create_category(db, name)

@router.get("/categories/")
def read_categories(skip: int = 0, limit: int = 100, db: Session = Depends(database.get_db)):
    categories = mod.get_categories(db, skip=skip, limit=limit)
    return categories

@router.delete("/categories/{category_id}/")
def delete_category(category_id: int, db: Session = Depends(database.get_db)):
    return mod.delete_category(db, category_id)
