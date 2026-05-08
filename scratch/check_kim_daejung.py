import sqlite3, sys
sys.stdout.reconfigure(encoding='utf-8')
conn = sqlite3.connect('candidates.db')
cur = conn.cursor()
cur.execute('SELECT id, name_kr, profile_summary FROM candidates WHERE name_kr = "김대중" AND is_duplicate = 0')
row = cur.fetchone()
if row:
    print(f'ID: {row[0]}')
    print(f'profile_summary: {row[2]}')
else:
    print("Kim Dae-jung not found.")
conn.close()
