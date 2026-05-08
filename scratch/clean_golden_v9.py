import sqlite3, json, sys
sys.stdout.reconfigure(encoding='utf-8')

conn = sqlite3.connect('candidates.db')
cur = conn.cursor()

try:
    with open('golden_dataset_v8.json', 'r', encoding='utf-8') as f:
        golden = json.load(f)
except FileNotFoundError:
    print("Error: golden_dataset_v8.json not found.")
    sys.exit(1)

cleaned = []
removed = []

for q in golden:
    relevant_ids = q.get('relevant_ids', [])
    relevant_names = q.get('relevant_names', [])
    
    # DB에 존재하는지 확인
    all_exist = True
    for cid in relevant_ids:
        cur.execute('SELECT id FROM candidates WHERE id = ? AND is_duplicate = 0', (cid,))
        if not cur.fetchone():
            all_exist = False
            break
    
    if all_exist:
        cleaned.append(q)
    else:
        removed.append((q.get('query'), relevant_names))

conn.close()

with open('golden_dataset_v9.json', 'w', encoding='utf-8') as f:
    json.dump(cleaned, f, ensure_ascii=False, indent=2)

print(f'원본: {len(golden)}개 쿼리')
print(f'정제 후: {len(cleaned)}개 쿼리')
print(f'제거된 쿼리: {len(removed)}개')
print()
for q, names in removed:
    print(f'  제거: {q} → {names}')
