import json
import re
import sqlite3

def clean_name(raw):
    if not raw: return ""
    # Remove text in brackets like [LG CNS], (DevOps Engineer), etc.
    s = re.sub(r'\[.*?\]', '', raw)
    s = re.sub(r'\(.*?\)', '', s)
    # Remove specific words
    s = s.replace('이력서', '').replace('사본', '').replace('복사본', '')
    # Remove numbers and special characters
    s = re.sub(r'[^가-힣A-Za-z]', '', s)
    return s.strip()

def analyze_duplicates():
    with open('candidates_cache_jd.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    names_map = {}
    for c in data:
        raw = c.get('name_kr', '')
        clean = clean_name(raw)
        
        if not clean: continue
        
        if clean not in names_map:
            names_map[clean] = []
        names_map[clean].append({
            'raw': raw,
            'id': c.get('id'),
            'summary_len': len(c.get('summary', '') or ''),
            'sectors_len': len(c.get('main_sectors', []) or [])
        })

    dups = {k: v for k, v in names_map.items() if len(v) > 1}
    print(f"Found {len(dups)} names with multiple records (ghost shells possible)")
    
    # Print examples
    count = 0
    for k, v in dups.items():
        print(f"Name: {k}")
        for x in v:
            print(f"  - {x['raw']} (UUID: {x['id']}, Data len: {x['summary_len']}, Sectors: {x['sectors_len']})")
        count += 1
        if count >= 3: break

if __name__ == "__main__":
    analyze_duplicates()
