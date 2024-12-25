from fastapi import FastAPI
from .api import router as api_router

app = FastAPI()

# Включаем маршруты API
app.include_router(api_router)
