import os
import psycopg2

CONFIG = {
    "dbname":"musicplayer7",
    "user":"postgres",
    "password":os.environ.get("PSQL_PASSWORD"),
    "host":"localhost",
    "port":5432,
}

def connect_db(dbname):

    temp_config = CONFIG.copy()
    temp_config["dbname"] = "postgres"

    conn = psycopg2.connect(**temp_config)
    conn.autocommit = True
    cur = conn.cursor()
    cur.execute("SELECT 1 FROM pg_database WHERE datname = %s;",(dbname,))

    exists = cur.fetchone() is not None
    
    if not exists:
        print(f"{dbname}が存在しないため作成します")

        cur.execute(f"CREATE DATABASE {dbname} WITH TEMPLATE template0 ENCODING 'UTF8' LC_COLLATE='C' LC_CTYPE='C';")

    cur.close()
    conn.close()
    return psycopg2.connect(**CONFIG)