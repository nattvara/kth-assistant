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

RUN huggingface-cli download mistralai/Mistral-7B-Instruct-v0.2
