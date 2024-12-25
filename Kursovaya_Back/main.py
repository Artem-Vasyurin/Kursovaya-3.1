from fastapi import FastAPI
from auth_service.api import router as auth_router
from mod_service.api import router as mod_router

app = FastAPI()

# Включаем маршруты API для обоих микросервисов
app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(mod_router, prefix="/mod", tags=["modifications"])
