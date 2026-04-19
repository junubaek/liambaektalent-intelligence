import sqlite3
import sys

sys.stdout.reconfigure(encoding='utf-8')
conn = sqlite3.connect('candidates.db')
cur = conn.cursor()

result = cur.execute('SELECT COUNT(*), COUNT(NULLIF(phone, "")), COUNT(NULLIF(email, "")) FROM candidates').fetchone()
print(f"Total: {result[0]}, Has Phone: {result[1]}, Has Email: {result[2]}")
