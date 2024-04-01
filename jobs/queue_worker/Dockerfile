FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PYTHONPATH=/app

WORKDIR /app

COPY requirements.txt ./

RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN python setup.py install

RUN playwright install chromium
RUN playwright install-deps

CMD ["sh", "-c", "rq worker --with-scheduler --url=\"redis://:@${REDIS_HOST}:${REDIS_PORT}\" \"${QUEUE_WORKER_QUEUE_NAME}\""]
