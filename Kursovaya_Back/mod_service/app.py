from fastapi import FastAPI
from . import models, database, api

app = FastAPI()

# Создаем все таблицы в базе данных
models.Base.metadata.create_all(bind=database.engine)

# Включаем маршруты из api.py
app.include_router(api.router)
