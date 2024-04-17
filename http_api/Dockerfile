FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PYTHONPATH=/app

WORKDIR /app

COPY requirements.txt ./

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    libpq-dev

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN python setup.py install

CMD ["sh", "-c", "migrate_up && uvicorn http_api:main --host 0.0.0.0 --port 80"]
