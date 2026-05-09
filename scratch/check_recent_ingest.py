import sqlite3
import sys

def check_recent():
    sys.stdout.reconfigure(encoding='utf-8')
    conn = sqlite3.connect('candidates.db')
    cur = conn.cursor()
    cur.execute("SELECT id, name_kr, created_at FROM candidates ORDER BY created_at DESC LIMIT 10")
    rows = cur.fetchall()
    for r in rows:
        print(r)
    conn.close()

if __name__ == "__main__":
    check_recent()
