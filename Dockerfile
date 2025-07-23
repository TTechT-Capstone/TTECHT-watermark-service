FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 5000

ENV PORT=5000
ENV WORKERS=3
ENV PYTHONUNBUFFERED=1

CMD gunicorn app:app --bind 0.0.0.0:$PORT --workers $WORKERS

