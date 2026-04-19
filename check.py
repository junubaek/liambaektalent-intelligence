import sqlite3

conn = sqlite3.connect('candidates.db')
c1 = conn.execute("SELECT name_kr FROM candidates WHERE name_kr LIKE '%여기어때%' OR name_kr LIKE '%자동화제%'").fetchall()
print("candidates:", c1)
conn.close()
