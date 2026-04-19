import sqlite3
import sys

conn = sqlite3.connect('C:/Users/cazam/Downloads/이력서자동분석검색시스템/candidates.db')
cursor = conn.cursor()

names = ['황성재', '김수희', '그룹', '정주원님', '서영호']
placeholders = ','.join('?' * len(names))
query = f"SELECT name_kr, length(raw_text) as text_len, id FROM candidates WHERE name_kr IN ({placeholders})"

cursor.execute(query, names)
rows = cursor.fetchall()

if not rows:
    print('No exact matches.')
else:
    for r in rows:
        print(f'{r[0]}, length: {r[1] if r[1] is not None else 0}, id: {r[2]}')

print('--- LIKE search ---')
query_like = "SELECT name_kr, length(raw_text) as text_len, id FROM candidates WHERE " + " OR ".join(["name_kr LIKE ?"] * len(names))
params = [f'%{n}%' for n in names]
cursor.execute(query_like, params)
for r in cursor.fetchall():
    print(f'{r[0]}, length: {r[1] if r[1] is not None else 0}, id: {r[2]}')
