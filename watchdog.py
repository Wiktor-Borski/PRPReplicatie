import time
import os
import smtplib
import psycopg
import requests
from email.mime.text import MIMEText
import logging
import sys
import os

# ---------------- CONFIG ---------------- #

logging.basicConfig(
    filename="/app/logs/watchdog.log",
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

CHECK_INTERVAL = 60

SENDER_URL = os.getenv("SENDER_URL", "http://sender:5000/replicate")

DB_HOST = os.getenv("DB_HOST", "postgres")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))

EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")
EMAIL_RECEIVER = os.getenv("EMAIL_RECEIVER")


# ---------------- EMAIL ---------------- #

def send_email(subject, message):
    msg = MIMEText(message)
    msg["Subject"] = subject
    msg["From"] = EMAIL_USER
    msg["To"] = EMAIL_RECEIVER

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_USER, EMAIL_PASS)
            server.send_message(msg)
    except Exception as e:
        logging.error(f"[EMAIL ERROR] {e}")


# ---------------- CHECKS ---------------- #

def check_sender():
    try:
        r = requests.get(SENDER_URL, timeout=5)

        if r.status_code in [200, 401]:
            return True

        return False

    except Exception:
        return False


def check_database():
    try:
        conn = psycopg.connect(
            host=DB_HOST,
            port=DB_PORT,
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
        )
        conn.close()
        return True
    except Exception:
        return False


# ---------------- MAIN LOOP ---------------- #

def run_watchdog():
    while True:
        sender_ok = check_sender()
        db_ok = check_database()

        if not sender_ok:
            send_email(
                "CRITICAL: Sender service down",
                "Sender service is not reachable via HTTP."
            )
            logging.error(f"[WATCHDOG] Sender service is down. email sent to {EMAIL_RECEIVER}.")

        if not db_ok:
            send_email(
                "CRITICAL: Database unreachable",
                "PostgreSQL database connection failed."
            )
            logging.error(f"[WATCHDOG] Database connection failed. email sent to {EMAIL_RECEIVER}.")

        logging.info(f"[WATCHDOG] sender={sender_ok} db={db_ok}")

        time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    run_watchdog()