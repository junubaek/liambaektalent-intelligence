import sqlite3

try:
    conn = sqlite3.connect('candidates.db')
    cursor = conn.cursor()
    cursor.execute("""
        SELECT name_kr, raw_text
        FROM candidates
        WHERE name_kr LIKE '%김대중%'
        LIMIT 1
    """)
    row = cursor.fetchone()
    if row:
        name, raw_text = row
        print(f"Name: {name}")
        
        # Look for keywords across the entire text before printing the first 1000 chars
        keywords = ["회계", "결산", "재무제표", "재무"]
        found = [kw for kw in keywords if raw_text and kw in raw_text]
        print(f"Keywords found anywhere in text: {found}\n")
        
        print("--- Raw Text (First 1500 chars) ---")
        print(raw_text[:1500] if raw_text else "None")
    else:
        print("Candidate not found in SQLite.")
except Exception as e:
    print(f"Database error: {e}")
finally:
    if 'conn' in locals():
        conn.close()
