import sqlite3
import json

conn = sqlite3.connect('candidates.db')
cur = conn.cursor()

names = ['김국현', '우형일', '한상현']
for name in names:
    cur.execute("SELECT name_kr, careers_json FROM candidates WHERE name_kr=? AND is_duplicate=0", (name,))
    row = cur.fetchone()
    if row:
        print(f"\n--- SQLite careers_json for '{row[0]}' ---")
        try:
            careers = json.loads(row[1]) if row[1] else []
            print(f"Careers count: {len(careers)}")
            if careers:
                print("First career keys:", careers[0].keys())
                for c in careers[:3]:
                    print(f"  Company: {c.get('company')} | Role: {c.get('title')}")
                    if 'skills' in c:
                        print(f"    skills: {c.get('skills')}")
                    if 'skills_used' in c:
                        print(f"    skills_used: {c.get('skills_used')}")
        except Exception as e:
            print("Error loading careers_json:", e)
            
conn.close()
