FROM python:3.13-slim

WORKDIR /app

COPY main.py /app/main.py

RUN pip install --no-cache-dir flask psycopg[binary]
RUN pip install --no-cache-dir python-dotenv

EXPOSE 5000

CMD ["python3", "main.py"]
