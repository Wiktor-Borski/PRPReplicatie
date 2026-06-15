FROM python:3.13-slim

WORKDIR /app

RUN pip install psycopg[binary] requests
RUN pip install --no-cache-dir python-dotenv

COPY watchdog.py /app/watchdog.py

CMD ["python3", "watchdog.py"]