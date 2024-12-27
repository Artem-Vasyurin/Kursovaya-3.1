# stats_service/models.py
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from stats_service.database import Base
from datetime import datetime

class UserStatistics(Base):
    __tablename__ = "user_statistics"

    id = Column(Integer, primary_key=True, autoincrement=True)
    event = Column(String, nullable=False)  # Название события
    name = Column(String, nullable=False)   # Имя пользователя
    time = Column(DateTime, default=datetime.utcnow)  # Время события

class ModStatistics(Base):
    __tablename__ = "mod_statistics"

    id = Column(Integer, primary_key=True, autoincrement=True)
    action = Column(String, nullable=False)  # Действие (например, загрузка)
    mod_name = Column(String, nullable=False)  # Название мода
    time = Column(DateTime, default=datetime.utcnow)  # Время события
