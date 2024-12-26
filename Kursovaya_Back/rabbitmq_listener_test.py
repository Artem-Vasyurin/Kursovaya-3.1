# -*- coding: utf-8 -*-

from pika import BlockingConnection, ConnectionParameters

connection_params = ConnectionParameters(
    host='localhost',  # Используйте 'rabbitmq', если контейнеры в одной сети
    port=5672,
)

def callback(ch, method, properties, body):
    print(f"Получено сообщение: {body.decode()}")

def start_rabbitmq_listener():
    print("Попытка подключиться к RabbitMQ...")
    try:
        with BlockingConnection(connection_params) as conn:
            print("Соединение с RabbitMQ установлено.")
            with conn.channel() as channel:
                print("Канал создан. Проверяем очередь...")
                channel.queue_declare(queue='user_queue', durable=True)
                print("Очередь user_queue объявлена.")

                print("Настроен слушатель, ожидаем сообщений...")
                channel.basic_consume(
                    queue='user_queue',
                    on_message_callback=callback,
                    auto_ack=True
                )
                print("Начало прослушивания сообщений из очереди.")
                channel.start_consuming()
    except Exception as e:
        print(f"Ошибка в слушателе RabbitMQ: {e}")

if __name__ == '__main__':
    start_rabbitmq_listener()
