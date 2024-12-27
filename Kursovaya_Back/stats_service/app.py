from fastapi import FastAPI
from threading import Thread
from stats_service.rabbitmq_listener import start_rabbitmq_listener

app = FastAPI()


async def lifespan(app: FastAPI):
    # Запускаем RabbitMQ слушателя в отдельном потоке при старте приложения
    listener_thread = Thread(target=start_rabbitmq_listener, daemon=True)
    listener_thread.start()
    print("Statistics microservice is running.")

    yield  # Эта строка завершит обработку после завершения работы приложения


app = FastAPI(lifespan=lifespan)