# stats_service/models.py
from sqlalchemy import Column, Integer, DateTime
from sqlalchemy.sql import func
from auth_service.database import Base
from datetime import datetime


class UserStatistics(Base):
    __tablename__ = "user_statistics"

    id = Column(Integer, primary_key=True)
    registrations = Column(Integer, default=0)
    last_update = Column(DateTime, default=datetime.utcnow)

    def increment_registrations(self):
        self.registrations += 1
        self.last_update = datetime.utcnow()