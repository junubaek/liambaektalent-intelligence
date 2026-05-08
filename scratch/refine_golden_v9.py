import sqlite3
import json
import sys

# Ensure UTF-8 output
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

conn = sqlite3.connect('candidates.db')
cur = conn.cursor()

with open('golden_dataset_v8.json', 'r', encoding='utf-8') as f:
    golden = json.load(f)

cleaned = []
removed_list = []

for q in golden:
    rel_ids = q.get('relevant_ids', [])
    rel_names = q.get('relevant_names', [])
    
    # 해당 쿼리의 모든 정답 후보자가 DB에 있는지 확인
    found_all = True
    missing_names = []
    for cid in rel_ids:
        cur.execute('SELECT name_kr FROM candidates WHERE id = ?', (cid,))
        row = cur.fetchone()
        if not row:
            found_all = False
            # 이름으로도 한번 더 찾아봄 (ID가 바뀌었을 수 있음)
            # 만약 이름으로 찾으면 그 ID로 교체해주면 좋겠지만, 일단은 제거 대상으로 분류
            missing_names.append(cid)
    
    if found_all:
        cleaned.append(q)
    else:
        removed_list.append({
            'query': q.get('query'),
            'missing_ids': missing_names,
            'target_names': rel_names
        })

conn.close()

with open('golden_dataset_v9.json', 'w', encoding='utf-8') as f:
    json.dump(cleaned, f, ensure_ascii=False, indent=2)

print(f"--- Golden Dataset V9 Refinement ---")
print(f"Total Original: {len(golden)} queries")
print(f"Cleaned (V9): {len(cleaned)} queries")
print(f"Removed: {len(removed_list)} queries")

if removed_list:
    print("\nRemoved Queries Detail:")
    for item in removed_list:
        print(f"  - {item['query']} | Targets: {item['target_names']} | Missing IDs: {item['missing_ids']}")
