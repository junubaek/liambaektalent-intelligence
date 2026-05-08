import sqlite3, json, sys
sys.stdout.reconfigure(encoding='utf-8')

with open('golden_dataset_v9.json', 'r', encoding='utf-8') as f:
    golden = json.load(f)

conn = sqlite3.connect('candidates.db')
cur = conn.cursor()

# v8도 같이 업데이트
with open('golden_dataset_v8.json', 'r', encoding='utf-8') as f:
    golden_v8 = json.load(f)

def get_master_id(name):
    cur.execute('SELECT id FROM candidates WHERE name_kr = ? AND is_duplicate = 0', (name,))
    row = cur.fetchone()
    return row[0] if row else None

for dataset, fname in [(golden, 'golden_dataset_v9.json'), (golden_v8, 'golden_dataset_v10.json')]:
    updated = []
    for q in dataset:
        new_rel_ids = []
        rel_names = q.get('relevant_names', q.get('relevant', []))
        if not rel_names:
            continue
        if isinstance(rel_names[0], dict):
            rel_names = [r.get('name_kr','') for r in rel_names]
        for name in rel_names:
            mid = get_master_id(name)
            if mid:
                new_rel_ids.append(mid)
        q['relevant_ids'] = new_rel_ids
        updated.append(q)
    with open(fname, 'w', encoding='utf-8') as f:
        json.dump(updated, f, ensure_ascii=False, indent=2)
    print(f'{fname} 저장 완료')

conn.close()
