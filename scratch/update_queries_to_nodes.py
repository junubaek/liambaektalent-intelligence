import sys
import sqlite3
import json
import os

# Set encoding for output
sys.stdout.reconfigure(encoding='utf-8')

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import CANONICAL_MAP
from ontology_graph import CANONICAL_MAP
CANONICAL_LOWER = {k.lower(): v for k, v in CANONICAL_MAP.items() if len(k) > 2}

DATASET_PATH = 'golden_dataset_v7.json'
DB_PATH = 'candidates.db'

if not os.path.exists(DATASET_PATH):
    print(f"Error: {DATASET_PATH} not found.")
    sys.exit(1)

with open(DATASET_PATH, 'r', encoding='utf-8') as f:
    d = json.load(f)

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

print(f"Replacing queries in {DATASET_PATH} with TOP 3 nodes...")

updated = 0
for item in d:
    ids = item.get('relevant_ids', [])
    if not ids:
        continue
    
    cur.execute('SELECT raw_text FROM candidates WHERE id=?', (ids[0],))
    row = cur.fetchone()
    if not row:
        continue
    
    raw_lower = (row[0] or '').lower()
    freq = {}
    for src, tgt in CANONICAL_LOWER.items():
        if src in raw_lower:
            freq[tgt] = freq.get(tgt, 0) + 1
    
    top3 = sorted(freq, key=lambda x: -freq[x])[:3]
    if top3:
        new_query = ' '.join(top3)
        item['query'] = new_query
        updated += 1

conn.close()

with open(DATASET_PATH, 'w', encoding='utf-8') as f:
    json.dump(d, f, ensure_ascii=False, indent=2)

print(f'\n{updated}개 쿼리 업데이트 완료 → {DATASET_PATH}')
for item in d:
    print(f"  {item['query']}")
