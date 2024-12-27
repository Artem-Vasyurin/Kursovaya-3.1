from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Modification(Base):
    __tablename__ = 'modifications'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(Text)
    created_at = Column(Integer)  # timestamp
    updated_at = Column(Integer)  # timestamp
    category_id = Column(Integer, ForeignKey('categories.id'))
    file_path = Column(String)  # Добавляем поле для хранения пути к файлу

    category = relationship("Category", back_populates="modifications")

class Category(Base):
    __tablename__ = 'categories'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)

    modifications = relationship("Modification", back_populates="category")