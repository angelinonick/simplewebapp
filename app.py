from flask import Flask
import psycopg2
import redis
import os

app = Flask(__name__)

# Environment variables for DB and Redis
POSTGRES_HOST = os.environ.get("POSTGRES_HOST", "db")
POSTGRES_PORT = int(os.environ.get("POSTGRES_PORT", 5432))
POSTGRES_DB = os.environ.get("POSTGRES_DB", "testdb")
POSTGRES_USER = os.environ.get("POSTGRES_USER", "postgres")
POSTGRES_PASSWORD = os.environ.get("POSTGRES_PASSWORD", "postgres")

REDIS_HOST = os.environ.get("REDIS_HOST", "redis")
REDIS_PORT = int(os.environ.get("REDIS_PORT", 6379))

# Connect to Redis
cache = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0)

# Connect to PostgreSQL
def get_db_conn():
    return psycopg2.connect(
        host=POSTGRES_HOST,
        port=POSTGRES_PORT,
        database=POSTGRES_DB,
        user=POSTGRES_USER,
        password=POSTGRES_PASSWORD
    )

# Ensure table exists
def init_db():
    conn = get_db_conn()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id SERIAL PRIMARY KEY,
            content TEXT
        )
    """)
    conn.commit()
    cur.close()
    conn.close()

@app.route("/")
def index():
    # Check Redis cache first
    cached = cache.get("messages")
    if cached:
        return cached.decode()

    # Insert a message
    conn = get_db_conn()
    cur = conn.cursor()
    cur.execute("INSERT INTO messages (content) VALUES (%s)", ("hellotest",))
    conn.commit()

    # Read all messages
    cur.execute("SELECT content FROM messages")
    messages = [row[0] for row in cur.fetchall()]
    cur.close()
    conn.close()

    # Cache result in Redis
    result = "<br>".join(messages)
    cache.set("messages", result, ex=30)  # 30 seconds TTL
    return result

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000)
