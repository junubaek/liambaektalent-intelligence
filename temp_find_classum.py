import json

with open('candidates_cache_jd.json', 'r', encoding='utf-8') as f:
    cands = json.load(f)

for c in cands:
    if '클라썸' in c.get('name_kr', '') or '클라썸' in c.get('name', ''):
        print("ID:", c.get('id'))
        print("Name (KR):", c.get('name_kr'))
        print("Name:", c.get('name'))
        print("Email:", c.get('email'))
        print("Phone:", c.get('phone'))
        print("Careers:", json.dumps(c.get('parsed_career_json', []), ensure_ascii=False))
        text = c.get('raw_text', '') or c.get('summary', '')
        print("Snippet:", text[:500])
        print("="*50)
