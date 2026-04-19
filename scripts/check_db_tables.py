import sqlite3
import json

def check_db():
    conn = sqlite3.connect('candidates.db')
    tables = conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
    print("Tables:", tables)

    # Let's inspect Neo4j Cache if there is one
    with open('candidates_cache_jd.json', 'r', encoding='utf-8') as f:
        cache = json.load(f)
        
    emails = sum(1 for c in cache if c.get('email') and len(str(c['email'])) > 3)
    phones = sum(1 for c in cache if c.get('phone') and len(str(c['phone'])) > 3)
    summs = sum(1 for c in cache if c.get('profile_summary'))
    print(f"Cache emails: {emails}, phones: {phones}, sums: {summs} out of {len(cache)}")

    # Let's check a raw_text sample
    c = conn.execute("SELECT raw_text FROM candidates WHERE email IS NULL OR email = '' LIMIT 1").fetchone()
    if c and c[0]:
        print("Sample raw text of missing email:")
        print(c[0][:300])

if __name__ == "__main__":
    check_db()
