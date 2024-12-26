from passlib.context import CryptContext
from .rabbitmq import send_user_message, create_rabbitmq_channel
from .models import User
from .database import SessionLocal
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def register_user(user_data):
    # Создаем сессию базы данных
    db = SessionLocal()

    try:
        # Логика регистрации нового пользователя
        # Например, создание нового пользователя в базе данных:
        new_user = User(**user_data)  # создаем объект пользователя
        db.add(new_user)
        db.commit()

        # После успешной регистрации отправляем сообщение в RabbitMQ
        channel = create_rabbitmq_channel()  # Создаем канал для отправки сообщения
        send_user_message(channel, user_data)  # Отправляем данные о пользователе

        print(f"User {user_data['username']} registered and message sent to RabbitMQ.")
    except Exception as e:
        print(f"Error registering user: {e}")
        db.rollback()  # Если ошибка, откатываем транзакцию
    finally:
        db.close()  # Закрываем сессию базы данных