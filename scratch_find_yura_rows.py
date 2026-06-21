import sqlite3
import sys

sys.stdout.reconfigure(encoding='utf-8')
conn = sqlite3.connect('candidates.db')
cursor = conn.cursor()

cursor.execute("SELECT id, name_kr, current_company, sector, is_duplicate FROM candidates WHERE name_kr = '안유리'")
rows = cursor.fetchall()
print("=== All rows for 안유리 ===")
for r in rows:
    print(f"ID: {r[0]} | Name: {r[1]} | Company: {r[2]} | Sector: {r[3]} | IsDup: {r[4]}")

conn.close()
