from pika import BlockingConnection, ConnectionParameters
from sqlalchemy.orm import Session
from stats_service.database import SessionLocal
from stats_service.models import UserStatistics, ModStatistics
import json

connection_params = ConnectionParameters(
    host='localhost',  # Используйте 'rabbitmq', если контейнеры в одной сети
    port=5672,
)

def save_user_data(event, name):
    db: Session = SessionLocal()
    try:
        user_stat = UserStatistics(event=event, name=name)
        db.add(user_stat)
        db.commit()
    finally:
        db.close()

def save_mod_data(action, mod_name):
    db: Session = SessionLocal()
    try:
        mod_stat = ModStatistics(action=action, mod_name=mod_name)
        db.add(mod_stat)
        db.commit()
    finally:
        db.close()

def callback_user(ch, method, properties, body):
    try:
        data = json.loads(body)
        event = data.get("event")
        name = data.get("username")
        if event and name:
            save_user_data(event, name)
        print(f"User data saved: {data}")
    except Exception as e:
        print(f"Error processing user data: {e}")

def callback_mod(ch, method, properties, body):
    try:
        data = json.loads(body)
        action = data.get("action")
        mod_name = data.get("name")
        if action and mod_name:
            save_mod_data(action, mod_name)
        print(f"Mod data saved: {data}")
    except Exception as e:
        print(f"Error processing mod data: {e}")

def start_rabbitmq_listener():
    print("Попытка подключиться к RabbitMQ...")
    try:
        with BlockingConnection(connection_params) as conn:
            print("Соединение с RabbitMQ установлено.")
            with conn.channel() as channel:
                print("Канал создан. Проверяем очередь...")
                channel.queue_declare(queue='user_queue', durable=True)
                channel.queue_declare(queue='mod_queue', durable=True)

                print("Настроен слушатель, ожидаем сообщений...")
                channel.basic_consume(
                    queue='user_queue',
                    on_message_callback=callback_user,
                    auto_ack=True
                )
                channel.basic_consume(
                    queue='mod_queue',
                    on_message_callback=callback_mod,
                    auto_ack=True
                )
                print("Начало прослушивания сообщений из очередей.")
                channel.start_consuming()
    except Exception as e:
        print(f"Ошибка в слушателе RabbitMQ: {e}")
