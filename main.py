import os
import psycopg
from psycopg import sql
from flask import Flask, jsonify

app = Flask(__name__)


def get_db_connection():
    return psycopg.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", "5432"),
        dbname=os.getenv("DB_NAME", "mydatabase"),
        user=os.getenv("DB_USER", "myuser"),
        password=os.getenv("DB_PASSWORD", "mypassword"),
    )

@app.route('/replicate', methods=['GET'])
def replicate_data():
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT table_schema, table_name
                FROM information_schema.tables
                WHERE table_type = 'BASE TABLE'
                  AND table_schema NOT IN ('information_schema', 'pg_catalog')
                ORDER BY table_schema, table_name
                """
            )
            tables = cur.fetchall()
            statements = []

            for schema_name, table_name in tables:
                cur.execute(
                    """
                    SELECT column_name, data_type, is_nullable, column_default
                    FROM information_schema.columns
                    WHERE table_schema = %s AND table_name = %s
                    ORDER BY ordinal_position
                    """,
                    (schema_name, table_name),
                )
                columns = cur.fetchall()

                column_defs = []
                for column_name, data_type, is_nullable, column_default in columns:
                    column_sql = sql.SQL("{} {}").format(
                        sql.Identifier(column_name),
                        sql.SQL(data_type),
                    )
                    if column_default:
                        column_sql += sql.SQL(" DEFAULT {} ").format(sql.SQL(column_default))
                    if is_nullable == "NO":
                        column_sql += sql.SQL("NOT NULL")
                    column_defs.append(column_sql)

                statements.append(
                    sql.SQL("CREATE TABLE {}.{} ({})").format(
                        sql.Identifier(schema_name),
                        sql.Identifier(table_name),
                        sql.SQL(", ").join(column_defs),
                    ).as_string(conn) + ";"
                )

                cur.execute(
                    sql.SQL("SELECT * FROM {}.{}").format(
                        sql.Identifier(schema_name),
                        sql.Identifier(table_name),
                    )
                )
                rows = cur.fetchall()
                row_columns = [column[0] for column in cur.description]

                for row in rows:
                    statements.append(
                        sql.SQL("INSERT INTO {}.{} ({}) VALUES ({});").format(
                            sql.Identifier(schema_name),
                            sql.Identifier(table_name),
                            sql.SQL(", ").join(sql.Identifier(name) for name in row_columns),
                            sql.SQL(", ").join(sql.Literal(value) for value in row),
                        ).as_string(conn)
                    )

    return jsonify({"count": len(statements), "sql": statements})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)