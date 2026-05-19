FROM python:3.11-slim

WORKDIR /app/backend
COPY backend/requirements*.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/app /app/backend/app
COPY frontend /app/frontend

CMD ["celery", "-A", "app.workers.celery_app:celery_app", "worker", "--loglevel=INFO", "-Q", "cvfit"]
