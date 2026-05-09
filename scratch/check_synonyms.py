import json
import os
import sys

PROJECT_ROOT = r"C:\Users\cazam\Downloads\이력서자동분석검색시스템"
sys.path.append(PROJECT_ROOT)

from ontology_graph import CANONICAL_MAP

def check_synonyms():
    with open('backend/synonyms.json', 'r', encoding='utf-8') as f:
        syns = json.load(f)
        
    canonical_keys_lower = {k.lower() for k in CANONICAL_MAP.keys()}
    
    missing = []
    for group in syns:
        for s in group:
            if s.lower() not in canonical_keys_lower:
                missing.append(s)
                
    print(f"Total synonyms in json: {sum(len(g) for g in syns)}")
    print(f"Missing in CANONICAL_MAP: {len(missing)}")
    print("Examples of missing:")
    for m in missing[:30]:
        print(f"  - {m}")

if __name__ == "__main__":
    check_synonyms()
