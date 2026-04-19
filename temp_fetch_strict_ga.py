import os
import json
import re

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
CACHE_FILE = os.path.join(ROOT_DIR, "candidates_cache_jd.json")

with open(CACHE_FILE, "r", encoding="utf-8") as f:
    cands = json.load(f)

def calculate_years(careers):
    total_months = 0
    for c in careers:
        period = c.get('period', '')
        matches = re.findall(r'(\d{4})\.?(\d{1,2})?', period)
        if len(matches) >= 1:
            start_y = int(matches[0][0])
            start_m = int(matches[0][1]) if matches[0][1] else 1
            if '현재' in period or '재직' in period:
                end_y = 2024
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
# 엄격한 필터링 조건
ga_keywords = ['총무', 'general affairs']
leader_keywords = ['팀장', '실장', '본부장', '총괄', '파트장', '부장', '이사', '임원']

for cand in cands:
    careers = cand.get('parsed_career_json')
    if isinstance(careers, str):
        try: careers = json.loads(careers)
        except: careers = []
    if not careers: continue

    is_ga_leader = False
    
    for c in careers:
        t = str(c.get('team', '')).lower()
        p = str(c.get('position', '')).lower()
        
        # 팀이나 포지션명에 총무가 명확히 들어가는지 확인
        has_ga = any(kw in t or kw in p for kw in ga_keywords)
        # 포지션에 리더 직급이 들어가는지 확인
        has_leader = any(kw in p or kw in t for kw in leader_keywords)
        
        # 총무이면서 리더인 경력이 단 하나라도 있으면 합격
        if has_ga and has_leader:
            is_ga_leader = True
            break
            
    if not is_ga_leader:
        continue
    
    years = calculate_years(careers)
    if years >= 9.5:  # 약 10년차 이상
        results.append({
            'name': cand.get('name_kr'),
            'years': years,
            'careers': careers,
            'raw_preview': str(cand.get('raw_text', ''))[:300]
        })

results.sort(key=lambda x: x['years'], reverse=True)

print(f"Total Matches (Strict GA Leaders): {len(results)}\n")
for i, res in enumerate(results[:10]):
    print(f"[{i+1}위] {res['name']} (총 경력: {res['years']:.1f}년)")
    # Print only relevant careers to show parsing accuracy
    print(json.dumps(res['careers'], ensure_ascii=False, indent=2))
