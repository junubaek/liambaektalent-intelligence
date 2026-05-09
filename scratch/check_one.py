import sqlite3
import sys

def check_one(name):
    sys.stdout.reconfigure(encoding='utf-8')
    conn = sqlite3.connect('candidates.db')
    cur = conn.cursor()
    cur.execute('SELECT name_kr, current_company, phone, email FROM candidates WHERE name_kr = ?', (name,))
    print(cur.fetchone())
    conn.close()

if __name__ == "__main__":
    check_one("김한수")
