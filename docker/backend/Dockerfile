FROM python:3.11-slim

WORKDIR /app

COPY ../../requirements.txt .

COPY ../../backend/ .

RUN python3 -m pip install --upgrade pip \
  && pip install --no-cache-dir -r requirements.txt


EXPOSE 5000

ENTRYPOINT ["flask"]
CMD ["run", "--host=0.0.0.0"]
