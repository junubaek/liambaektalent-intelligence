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

print(f"Analyzing Top 3 nodes for anchors in {DATASET_PATH}...\n")

for item in d:
    q = item.get('query', '')
    ids = item.get('relevant_ids', [])
    if not ids:
        continue
    
    # 앵커(첫 번째 ID) 정보 가져오기
    cur.execute('SELECT name_kr, raw_text FROM candidates WHERE id=?', (ids[0],))
    row = cur.fetchone()
    if not row:
        continue
    
    name, raw = row
    raw_lower = (raw or '').lower()
    
    # 노드 빈도 계산
    freq = {}
    for src, tgt in CANONICAL_LOWER.items():
        if src in raw_lower:
            freq[tgt] = freq.get(tgt, 0) + 1
    
    # 빈도순 정렬 후 상위 3개 추출
    top3 = sorted(freq, key=lambda x: -freq[x])[:3]
    
    print(f'[{q}] {name}')
    print(f'  TOP3: {top3}')
    print()

conn.close()
