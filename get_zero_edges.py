import json
import sqlite3
import sys

sys.stdout.reconfigure(encoding='utf-8')

try:
    with open('processed_step6.json', 'r', encoding='utf-8') as f:
        d = json.load(f)
except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)

# Find candidates with 0 edges
zero_uids = [k for k, v in d.items() if v.get('edge_count', 0) == 0]

db = sqlite3.connect('candidates.db')
c = db.cursor()

names = []
for uid in zero_uids:
    c.execute('SELECT name_kr FROM candidates WHERE id=?', (uid,))
    row = c.fetchone()
    if row:
        names.append(row[0])
    
print(f"총 {len(names)}명의 엣지 0개 잔류 인원 명단:")
# Chunk to print nicely formatted
chunk_size = 10
for i in range(0, len(names), chunk_size):
    print(", ".join(names[i:i+chunk_size]))
