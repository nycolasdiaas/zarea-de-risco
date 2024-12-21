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

COPY pyproject.toml poetry.lock ./

COPY backend/ ./backend/

RUN poetry install --only main

EXPOSE 5000

CMD ["poetry", "run", "flask", "run", "--host=0.0.0.0", "--debug"]
