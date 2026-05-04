
import sys
import sqlite3
import json
import math
import os

# Set root directory
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT_DIR)
sys.stdout.reconfigure(encoding='utf-8')

from ontology_graph import CANONICAL_MAP

def generate_node_idf():
    # Only use keywords longer than 2 characters to avoid noise
    CANONICAL_LOWER = {k.lower(): v for k, v in CANONICAL_MAP.items() if len(k) > 2}

    conn = sqlite3.connect('candidates.db')
    cur = conn.cursor()
    cur.execute('SELECT raw_text FROM candidates WHERE raw_text IS NOT NULL')
    all_raws = cur.fetchall()
    conn.close()

    total = len(all_raws)
    if total == 0:
        print("Error: No candidates with raw_text found.")
        return

    node_df = {}
    print(f"Processing {total} candidates...")
    
    # Simple count of documents containing the keyword
    for i, (raw,) in enumerate(all_raws):
        if i % 500 == 0:
            print(f"  Processed {i}/{total}...")
        
        raw_lower = (raw or '').lower()
        found = set()
        # Find which canonical targets are present in this document
        for src, tgt in CANONICAL_LOWER.items():
            if src in raw_lower:
                found.add(tgt)
        
        for n in found:
            node_df[n] = node_df.get(n, 0) + 1

    # Calculate IDF
    node_idf = {n: math.log(total / df) for n, df in node_df.items()}
    
    # Save to JSON
    with open('node_idf.json', 'w', encoding='utf-8') as f:
        json.dump(node_idf, f, ensure_ascii=False, indent=2)
        
    print(f'\n총 {len(node_idf)}개 노드 IDF 계산 완료')
    
    print('상위 10개 (희귀한 노드):')
    for n, idf in sorted(node_idf.items(), key=lambda x: -x[1])[:10]:
        print(f'  {n}: {idf:.2f}')
        
    print('하위 10개 (흔한 노드):')
    for n, idf in sorted(node_idf.items(), key=lambda x: x[1])[:10]:
        print(f'  {n}: {idf:.2f}')

if __name__ == "__main__":
    generate_node_idf()
