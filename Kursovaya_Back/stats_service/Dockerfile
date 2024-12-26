FROM python:3.9

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

# Запуск FastAPI без --reload в продакшн-режиме
CMD ["uvicorn", "stats_service.main:app", "--host", "0.0.0.0", "--port", "8001"]
