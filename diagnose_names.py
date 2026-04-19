import sqlite3

def diagnose():
    conn = sqlite3.connect('candidates.db')
    cur = conn.cursor()
    
    # We want to match names that look like placeholders, parenthesized, or "미상"
    cur.execute("SELECT id, name_kr, document_hash, raw_text FROM candidates WHERE name_kr LIKE '%(%' OR name_kr LIKE '%미상%' OR name_kr='이름' OR name_kr='이름없음' OR name_kr='UX컨설팅' OR name_kr='가천대석' LIMIT 10")
    rows = cur.fetchall()
    
    for row in rows:
        print(f"=== Name in DB: {row[1]} ===")
        print(f"ID: {row[0]}")
        print(f"Doc Hash (Filename): {row[2]}")
        text = row[3] or ""
        print(f"Raw Text (first 60 chars): {text[:60].replace(chr(10), ' ')}")
        print("-" * 50)
        
    conn.close()

if __name__ == '__main__':
    diagnose()
