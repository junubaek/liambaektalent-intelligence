import sqlite3
import json

def check_careers():
    conn = sqlite3.connect('candidates.db')
    c = conn.execute("SELECT careers_json, education_json FROM candidates WHERE careers_json IS NOT NULL AND careers_json != '[]' LIMIT 5").fetchall()
    
    for row in c:
        print("Careers:", row[0][:200])
        print("Education:", row[1][:200] if row[1] else "None")
        print("-" * 50)

if __name__ == "__main__":
    check_careers()
