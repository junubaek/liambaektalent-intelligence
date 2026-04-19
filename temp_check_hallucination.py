import sys
sys.stdout.reconfigure(encoding='utf-8')
import json
from collections import Counter

with open('candidates_cache_jd.json', encoding='utf-8') as f:
    cands = json.load(f)

hallucinated = []
for c in cands:
    careers = c.get('parsed_career_json') or []
    if isinstance(careers, str):
        try:
            careers = json.loads(careers)
        except:
            careers = []
    
    companies = [x.get('company','') for x in careers if isinstance(x, dict) and x.get('company')]
    dupes = [co for co, cnt in Counter(companies).items() if cnt >= 2]
    if dupes:
        hallucinated.append({
            'id': c.get('id'),
            'name': c.get('name_kr'),
            'dupes': dupes,
            'count': sum(1 for x in companies if x in dupes)
        })

print(f'할루시네이션 감지: {len(hallucinated)}명')
print(f'상위 10명:')
for h in sorted(hallucinated, key=lambda x: -x['count'])[:10]:
    print(f"  {h['name']} - 중복 회사: {h['dupes']}")
