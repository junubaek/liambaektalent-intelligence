import json, sqlite3, sys
sys.stdout.reconfigure(encoding='utf-8')

with open('golden_dataset_v8.json', encoding='utf-8') as f:
    data = json.load(f)
conn = sqlite3.connect('candidates.db')
cur = conn.cursor()
print(f'쿼리 수: {len(data)}')
bad = 0
for q in data:
    for rid in q.get('relevant_ids', []):
        cur.execute('SELECT is_duplicate FROM candidates WHERE id=?', (rid,))
        r = cur.fetchone()
        if r is None or r[0] == 1:
            bad += 1
            print(f'  문제: {q["query"][:20]} | {rid[:8]}')
print(f'문제 ID 수: {bad}')
conn.close()
