import psycopg2
from datetime import datetime

def get_connection():
    return psycopg2.connect(
        host="localhost",
        port=5433,
        dbname="aishield",
        user="postgres",
        password="shieldpass123"
    )

def init_db():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS blocked_events (
            id SERIAL PRIMARY KEY,
            ip TEXT NOT NULL,
            path TEXT NOT NULL,
            reason TEXT NOT NULL,
            timestamp TIMESTAMP NOT NULL
        )
    """)
    conn.commit()
    cur.close()
    conn.close()

def log_block(ip: str, path: str, reason: str):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO blocked_events (ip, path, reason, timestamp) VALUES (%s, %s, %s, %s)",
        (ip, path, reason, datetime.now())
    )
    conn.commit()
    cur.close()
    conn.close()

def get_all_blocks():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, ip, path, reason, timestamp FROM blocked_events ORDER BY timestamp DESC")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows