from fastapi import FastAPI
from .api import router as api_router
from .rabbitmq import create_rabbitmq_channel, close_connection

app = FastAPI()

# Включаем маршруты API
app.include_router(api_router)

@app.on_event("shutdown")
def shutdown_rabbitmq():
    close_connection()  # Закрываем соединение с RabbitMQ при завершении работы
