import json
import sys
sys.stdout.reconfigure(encoding='utf-8')
from collections import Counter

with open('candidates_cache_jd.json', encoding='utf-8') as f:
    cands = json.load(f)

hallucinated = []
for c in cands:
    careers = c.get('parsed_career_json') or []
    companies = [x.get('company','') for x in careers if x.get('company')]
    dupes = [co for co, cnt in Counter(companies).items() if cnt >= 2]
    if dupes:
        count_dupes = sum(cnt for co, cnt in Counter(companies).items() if cnt >= 2)
        hallucinated.append({
            'id': c.get('id'),
            'name': c.get('name_kr'),
            'dupes': dupes,
            'count': count_dupes
        })

print(f'할루시네이션 감지: {len(hallucinated)}명')
print(f'상위 10명:')
for h in sorted(hallucinated, key=lambda x: -x['count'])[:10]:
    print(f"  {h['name']} — 중복 발생 블록 수: {h['count']}회, 중복 회사명: {h['dupes']}")
