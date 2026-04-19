import sqlite3
import builtins

conn = sqlite3.connect('candidates.db')
cursor = conn.cursor()
cursor.execute('SELECT id, name_kr, raw_text FROM candidates LIMIT 10')
with open('raw_text_samples.txt', 'w', encoding='utf-8') as f:
    for row in cursor.fetchall():
        f.write(f'=== ID: {row[0]} 현재이름: {row[1]}\n')
        f.write(row[2][:500] if row[2] else '없음')
        f.write('\n\n')
conn.close()
