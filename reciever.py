import json
import os
from urllib import error, request

import psycopg


SOURCE_URL = os.getenv("SOURCE_URL", "http://192.168.122.18:5000/replicate")
TARGET_DB_HOST = os.getenv("TARGET_DB_HOST", "target-postgres")
TARGET_DB_PORT = os.getenv("TARGET_DB_PORT", "5432")
TARGET_DB_NAME = os.getenv("TARGET_DB_NAME", "mydatabase")
TARGET_DB_USER = os.getenv("TARGET_DB_USER", "myuser")
TARGET_DB_PASSWORD = os.getenv("TARGET_DB_PASSWORD", "mypassword")


def fetch_sql_statements():
	http_request = request.Request(
		SOURCE_URL,
		headers={"Content-Type": "application/json"},
	)

	with request.urlopen(http_request, timeout=60) as response:
		data = json.loads(response.read().decode("utf-8"))

	statements = data.get("sql", [])
	if not isinstance(statements, list):
		raise ValueError("Expected 'sql' to be a list of SQL statements")

	return statements


def apply_sql_statements(statements):
	with psycopg.connect(
		host=TARGET_DB_HOST,
		port=TARGET_DB_PORT,
		dbname=TARGET_DB_NAME,
		user=TARGET_DB_USER,
		password=TARGET_DB_PASSWORD,
	) as conn:
		with conn.cursor() as cur:
			for statement in statements:
				if statement and statement.strip():
					cur.execute(statement)


def main():
	try:
		statements = fetch_sql_statements()
		apply_sql_statements(statements)
		print(f"Applied {len(statements)} SQL statements to {TARGET_DB_NAME}.")
	except (error.URLError, error.HTTPError, ValueError, psycopg.Error) as exc:
		raise SystemExit(f"Replication failed: {exc}") from exc


if __name__ == "__main__":
	main()
