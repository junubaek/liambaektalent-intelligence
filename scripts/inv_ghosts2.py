import sqlite3
import json

def investigate2():
    conn = sqlite3.connect('candidates.db')
    c = conn.execute("SELECT name_kr, id, careers_json, raw_text FROM candidates WHERE name_kr IN ('장형준', '최예리', '임정훈', '정준수')").fetchall()
    for row in c:
        print(f"Name: {row[0]}, ID: {row[1]}")
        print(f" Careers: {row[2][:50] if row[2] else 'None'}")
        print(f" Raw Text Length: {len(row[3]) if row[3] else 0}")
        print("-" * 20)

if __name__ == "__main__":
    investigate2()
