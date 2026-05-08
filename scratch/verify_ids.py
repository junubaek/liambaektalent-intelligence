import sqlite3
import json
import sys
import os

# Set encoding for output
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

dataset_path = 'golden_dataset_v8.json'
if not os.path.exists(dataset_path):
    print(f"Error: {dataset_path} not found.")
    sys.exit(1)

with open(dataset_path, 'r', encoding='utf-8') as f:
    golden = json.load(f)

conn = sqlite3.connect('candidates.db')
cur = conn.cursor()

total_ids = 0
matched = 0
unmatched_names = []

for query_data in golden:
    rel_ids = query_data.get('relevant_ids', [])
    rel_names = query_data.get('relevant_names', [])
    
    # Map name to ID if possible (assuming they are in order, which is common in these datasets)
    # If not in order, we'll just check all.
    for i, cid in enumerate(rel_ids):
        name = rel_names[i] if i < len(rel_names) else "Unknown"
        total_ids += 1
        
        # Check by ID
        cur.execute('SELECT id, name_kr FROM candidates WHERE id = ?', (cid,))
        row = cur.fetchone()
        if row:
            matched += 1
        else:
            # Check by Name
            cur.execute('SELECT id, name_kr FROM candidates WHERE name_kr = ? AND is_duplicate = 0', (name,))
            row2 = cur.fetchone()
            if row2:
                unmatched_names.append((name, cid, row2[0]))
            else:
                unmatched_names.append((name, cid, None))

conn.close()
print(f'전체 ID: {total_ids}개')
print(f'ID 직접 매칭: {matched}개')
print(f'ID 불일치: {total_ids - matched}개')
print()
print('불일치 샘플 (Dataset ID vs DB ID):')
for name, old_id, new_id in unmatched_names[:20]:
    print(f'  {name} | Dataset: {old_id[:8]}... | DB: {new_id[:8] if new_id else "없음"}...')
