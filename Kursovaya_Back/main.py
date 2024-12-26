from fastapi import FastAPI
from auth_service.api import router as auth_router
from mod_service.api import router as mod_router
from stats_service.api import router as stat_router
from stats_service.rabbitmq_listener import start_rabbitmq_listener
from threading import Thread
import uvicorn

app = FastAPI()

# Включаем маршруты API для всех микросервисов
app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(mod_router, prefix="/mod", tags=["modifications"])
app.include_router(stat_router, prefix="/stat", tags=["statistics"])

# Функция для запуска RabbitMQ listener в отдельном потоке
def run_rabbitmq_listener():
    start_rabbitmq_listener()

@app.on_event("startup")
async def startup():
    print("Запуск приложения.")
    listener_thread = Thread(target=run_rabbitmq_listener, daemon=True)
    listener_thread.start()

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
