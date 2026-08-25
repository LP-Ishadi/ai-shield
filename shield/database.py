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

def get_blocks_grouped(period="hour"):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(f"""
        SELECT date_trunc(%s, timestamp) AS period, COUNT(*) 
        FROM blocked_events 
        GROUP BY period 
        ORDER BY period
    """, (period,))
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows

def get_threat_levels(ip_filter=None):
    conn = get_connection()
    cur = conn.cursor()
    if ip_filter:
        cur.execute("""
            SELECT ip, COUNT(*) as block_count
            FROM blocked_events
            WHERE ip LIKE %s
            GROUP BY ip
            ORDER BY block_count DESC
        """, (f"%{ip_filter}%",))
    else:
        cur.execute("""
            SELECT ip, COUNT(*) as block_count
            FROM blocked_events
            GROUP BY ip
            ORDER BY block_count DESC
        """)
    rows = cur.fetchall()
    cur.close()
    conn.close()

    threats = []
    for ip, count in rows:
        if count >= 4:
            level = "High"
        elif count >= 2:
            level = "Medium"
        else:
            level = "Low"
        threats.append((ip, count, level))
    return threats

def search_blocks(ip_filter=None):
    conn = get_connection()
    cur = conn.cursor()
    if ip_filter:
        cur.execute(
            "SELECT id, ip, path, reason, timestamp FROM blocked_events WHERE ip LIKE %s ORDER BY timestamp DESC",
            (f"%{ip_filter}%",)
        )
    else:
        cur.execute("SELECT id, ip, path, reason, timestamp FROM blocked_events ORDER BY timestamp DESC")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows