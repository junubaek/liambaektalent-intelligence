import sqlite3
import os

def check_db():
    try:
        db = os.environ.get('DB_PATH', '/data/candidates.db')
        if not os.path.exists(db):
            print(f"[{__file__}] Database file not found at {db}")
            return
            
        print(f"[{__file__}] Checking Railway DB at {db}...")
        conn = sqlite3.connect(db)
        cur = conn.cursor()
        
        cur.execute("SELECT COUNT(*) FROM candidates WHERE name_kr LIKE 'CANDIDATE_%'")
        count = cur.fetchone()[0]
        print(f"=== RAILWAY DB CHECK: CANDIDATE_ 패턴: {count} ===")
        
        cur.execute("SELECT id, name_kr FROM candidates WHERE name_kr LIKE 'CANDIDATE_%' LIMIT 5")
        for r in cur.fetchall():
            print(f"ID: {r[0][:8]}, NAME: {r[1]}")
            
        conn.close()
    except Exception as e:
        print(f"[{__file__}] Error checking Railway DB: {e}")

if __name__ == "__main__":
    check_db()
