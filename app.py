import time
import psycopg2
from flask import Flask

app = Flask(__name__)

DB_CONFIG = {
    "host": "db",
    "user": "user",
    "password": "password",
    "database": "mydb"
}

def get_db_conn(retries=10, delay=10):
    for i in range(retries):
        try:
            return psycopg2.connect(**DB_CONFIG)
        except psycopg2.OperationalError:
            print(f"DB not ready, retrying ({i+1}/{retries})...")
            time.sleep(delay)
    raise Exception("DB not ready after multiple retries")

def init_db():
    conn = get_db_conn()
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS test(id SERIAL PRIMARY KEY, name TEXT);")
    conn.commit()
    cursor.close()
    conn.close()

@app.route("/")
def index():
    return "Web app is running!"

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000)

