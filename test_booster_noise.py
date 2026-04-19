import sqlite3
import re
from ontology_graph import CANONICAL_MAP

def scan_booster(raw_text):
    raw_lower = raw_text.lower()
    SCAN_KEYWORDS = list(CANONICAL_MAP.keys())
    
    booster_hits = set()
    mapped_hits = {}
    
    for keyword in SCAN_KEYWORDS:
        if len(keyword) < 2: continue
        canonical = CANONICAL_MAP[keyword]
        
        pattern = r'\b' + re.escape(keyword.lower()) + r'\b'
        if re.search(pattern, raw_lower):
            booster_hits.add(canonical)
            if canonical not in mapped_hits:
                mapped_hits[canonical] = []
            mapped_hits[canonical].append(keyword)
            
    return mapped_hits

def main():
    conn = sqlite3.connect('candidates.db')
    c = conn.cursor()
    
    print("=== 1. 최호진 Booster Scan Results ===")
    row = c.execute('SELECT raw_text FROM candidates WHERE name_kr="최호진"').fetchone()
    if row and row[0]:
        hits = scan_booster(row[0])
        print(f"Total Booster Unique Canonical Nodes: {len(hits)}")
        for canon, keys in hits.items():
            print(f" - {canon} (Matched by: {keys})")
    
    # 2. 테스트용 후보자 (단순한 후보자: 이상욱)
    print("\n=== 2. 이상욱 Booster Scan Results ===")
    row = c.execute('SELECT raw_text FROM candidates WHERE name_kr="이상욱"').fetchone()
    if row and row[0]:
        hits = scan_booster(row[0])
        print(f"Total Booster Unique Canonical Nodes: {len(hits)}")
        for canon, keys in hits.items():
            print(f" - {canon} (Matched by: {keys})")
    else:
        print("이상욱 not found.")

    conn.close()

if __name__ == '__main__':
    main()
