import sqlite3
import os

DB_PATH = "deals.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("CREATE TABLE IF NOT EXISTS deals (deal_id TEXT PRIMARY KEY, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)")
    conn.commit()
    conn.close()

def is_new_deal(deal_id):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT 1 FROM deals WHERE deal_id = ?", (deal_id,))
    exists = cur.fetchone()
    conn.close()
    return exists is None

def save_deal(deal_id):
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.execute("INSERT INTO deals (deal_id) VALUES (?)", (deal_id,))
        conn.commit()
        conn.close()
    except sqlite3.IntegrityError:
        pass # Already exists
