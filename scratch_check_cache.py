import json
with open('candidates_cache_jd.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
with open('scratch_kim.txt', 'w', encoding='utf-8') as f:
    for c in data:
        if '김효민' in c.get('name_kr', ''):
            f.write(f"name: {c.get('name_kr')}, company: {c.get('current_company')}, years: {c.get('total_years')}, seniority: {c.get('seniority')}\n")
