from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from stats_service.models import UserStatistics
from stats_service.database import get_db

router = APIRouter()

@router.get("/statistics")
def get_statistics(db: Session = Depends(get_db)):
    stats = db.query(UserStatistics).first()
    if not stats:
        # Если записи нет, возвращаем сообщение
        return {"registrations": 0, "last_update": None}
    return {
        "registrations": stats.registrations,
        "last_update": stats.last_update
    }
