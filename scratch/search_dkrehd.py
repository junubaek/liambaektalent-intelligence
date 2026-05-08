import sqlite3, sys
sys.stdout.reconfigure(encoding='utf-8')
conn = sqlite3.connect('candidates.db')
cur = conn.cursor()
cur.execute('SELECT id, name_kr, google_drive_url FROM candidates WHERE raw_text LIKE "%dkrehd%"')
rows = cur.fetchall()
if rows:
    print(f"Found {len(rows)} records containing 'dkrehd':")
    for r in rows:
        print(f"  ID: {r[0]} | Name: {r[1]} | URL: {r[2]}")
else:
    print("No records found containing 'dkrehd'.")
conn.close()
