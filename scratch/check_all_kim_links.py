import sqlite3, sys
sys.stdout.reconfigure(encoding='utf-8')
conn = sqlite3.connect('candidates.db')
cur = conn.cursor()
cur.execute('SELECT id, name_kr, google_drive_url, current_company FROM candidates WHERE name_kr = "김영민"')
rows = cur.fetchall()
if rows:
    print(f"Found {len(rows)} records for 김영민:")
    for r in rows:
        print(f"  ID: {r[0]} | Name: {r[1]} | Company: {r[3]} | URL: {r[2]}")
else:
    print("No records found for 김영민.")
conn.close()
