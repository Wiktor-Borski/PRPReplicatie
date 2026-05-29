FROM python:3.13-slim

WORKDIR /app

COPY reciever.py /app/reciever.py

RUN pip install --no-cache-dir psycopg[binary]

CMD ["python3", "reciever.py"]
