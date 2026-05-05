import sqlite3
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

conn = sqlite3.connect('candidates.db')
cur = conn.cursor()
cur.execute("SELECT id, name_kr, is_duplicate, current_company, total_years, profile_summary, careers_json FROM candidates WHERE name_kr LIKE '%김은형%'")
rows = cur.fetchall()

for row in rows:
    print(f"ID: {row[0]}, Name: {row[1]}, Duplicate: {row[2]}, Company: {row[3]}, Total Years: {row[4]}")
    print(f"Summary: {row[5][:100]}...")
    try:
        careers = json.loads(row[6]) if row[6] else []
        print(f"Career Count: {len(careers)}")
        if careers:
            print(f"Latest Career: {careers[0]}")
    except:
        print("Career JSON Parse Error")
    print("-" * 50)
conn.close()
