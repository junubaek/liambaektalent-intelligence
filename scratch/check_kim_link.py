import sqlite3, sys
sys.stdout.reconfigure(encoding='utf-8')
conn = sqlite3.connect('candidates.db')
cur = conn.cursor()
cur.execute('SELECT google_drive_url FROM candidates WHERE name_kr = "김영민" AND is_duplicate = 0')
row = cur.fetchone()
if row:
    print(f'Google Drive URL: {row[0]}')
else:
    print("Candidate Kim Young-min not found.")
conn.close()
