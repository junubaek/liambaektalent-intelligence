import os
import json
import re
from datetime import datetime

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
CACHE_FILE = os.path.join(ROOT_DIR, "candidates_cache_jd.json")

with open(CACHE_FILE, "r", encoding="utf-8") as f:
    cands = json.load(f)

def calculate_years(careers):
    total_months = 0
    for c in careers:
        period = c.get('period', '')
        # Example: '2019.05 ~ 현재', '2015.07 ~ 2020.03'
        matches = re.findall(r'(\d{4})\.?(\d{1,2})?', period)
        if len(matches) >= 1:
            start_y = int(matches[0][0])
            start_m = int(matches[0][1]) if matches[0][1] else 1
            
            if '현재' in period or '재직' in period:
                end_y = 2024 # Current reference year
                end_m = 6
            elif len(matches) >= 2:
                end_y = int(matches[1][0])
                end_m = int(matches[1][1]) if matches[1][1] else 1
            else:
                continue
                
            months = (end_y - start_y) * 12 + (end_m - start_m)
            if months > 0:
                total_months += months
    return total_months / 12.0

results = []
ga_keywords = ['총무', 'general affairs', 'ga팀', '경영지원']
leader_keywords = ['팀장', '리더', '파트장', '실장', '본부장', 'head', 'lead', '총괄', '매니저']

for cand in cands:
    careers = cand.get('parsed_career_json')
    if isinstance(careers, str):
        try: careers = json.loads(careers)
        except: careers = []
    if not careers: continue

    raw_text = (str(cand.get('raw_text', '')) + str(cand.get('summary', ''))).lower()
    
    # Text or careers must contain GA
    has_ga = any(kw in raw_text for kw in ga_keywords)
    for c in careers:
        role_text = (str(c.get('team') or '') + str(c.get('position') or '')).lower()
        if any(kw in role_text for kw in ga_keywords):
            has_ga = True
            break
            
    if not has_ga: continue
    
    # Leader
    has_leader = any(kw in raw_text for kw in leader_keywords)
    for c in careers:
        role_text = (str(c.get('team') or '') + str(c.get('position') or '')).lower()
        if any(kw in role_text for kw in leader_keywords):
            has_leader = True
            break
            
    if not has_leader: continue
    
    # Years
    years = calculate_years(careers)
    
    if years >= 9.0: # allow close to 10
        results.append({
            'name': cand.get('name_kr'),
            'years': years,
            'careers': careers,
            'raw_preview': raw_text[:200]
        })

results.sort(key=lambda x: x['years'], reverse=True)

print(f"Total Matches: {len(results)}")
for i, res in enumerate(results[:10]):
    print(f"\n[{i+1}위] {res['name']} (예상 경력: {res['years']:.1f}년)")
    print(json.dumps(res['careers'], ensure_ascii=False, indent=2))
