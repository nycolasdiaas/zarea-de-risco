FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    build-essential \
    libffi-dev \
    python3-dev \
    curl \
    && apt-get clean

RUN curl -sSL https://install.python-poetry.org | python3 -

ENV PATH="/root/.local/bin:$PATH"
ENV FLASK_APP="backend/app.py"
ENV FLASK_ENV="development"

WORKDIR /app

COPY pyproject.toml poetry.lock README.md ./

COPY backend/ ./backend/

RUN poetry lock &&\
    poetry install --only main

