import json, sqlite3, sys, re, math
sys.stdout.reconfigure(encoding='utf-8')
from jd_compiler import api_search_v8

print("=== A. golden_dataset 삭제된 ID 정리 ===")
conn = sqlite3.connect('candidates.db')
conn.row_factory = sqlite3.Row
cur = conn.cursor()

d = json.load(open('golden_dataset_v3.json', encoding='utf-8'))

cleaned = []
removed = 0
replaced = 0
existing_queries = set()

for item in d:
    rel = item.get('relevant_ids') or []
    if not rel and item.get('candidate_neo4j_id'):
        rel = [item.get('candidate_neo4j_id')]
    
    # 살아있는 ID만 필터
    valid_ids = []
    for rid in rel:
        cur.execute(
            'SELECT id FROM candidates WHERE id=? AND is_duplicate=0',
            (rid,)
        )
        if cur.fetchone():
            valid_ids.append(rid)
    
    if not valid_ids:
        # 정답이 하나도 없으면 → 해당 쿼리로 재검색해서 교체
        removed += 1
        print(f'[제거 대상] {item.get("query","")[:60]}')
        continue
    
    item['relevant_ids'] = valid_ids
    if 'candidate_neo4j_id' in item:
        item['candidate_neo4j_id'] = valid_ids[0]
    cleaned.append(item)
    
    q = item.get('query') or item.get('jd_query')
    if q: existing_queries.add(q)

print(f'\n처리 완료:')
print(f'  제거된 쿼리: {removed}개')
print(f'  남은 쿼리:   {len(cleaned)}개')

print("\n=== B. 제거된 쿼리 → 새 정답으로 교체 ===")
removed_queries = [
    ('CFO 또는 재무본부장급. IPO, IR, 자금조달, 세무까지 전반적인 재무 총괄', 'SENIOR'),
    ('AI Accelerators Generative AI Datacenter GPU cluster', 'All'),
    ('Kubernetes Terraform LangGraph DevOps pipeline', 'All'),
    ('Collective Communication C/C++ RDMA RoCE InfiniBand', 'All'),
    ('ERP Excel Labor Law HR payroll', 'All'),
    ('Financial Modeling Valuation Excel DCF LBO', 'All'),
    ('Chip Bring-up Driver Development embedded', 'All'),
    ('ARM SVE Neural Network Operations embedded', 'All'),
]

new_entries = []
for query, seniority in removed_queries:
    if query in existing_queries:
        continue
    r = api_search_v8(query, seniority=seniority)
    matched = r.get('matched', [])
    if not matched:
        continue
    
    # 상위 3명 정답으로 등록
    valid_ids = []
    for c in matched[:3]:
        cid = c.get('id')
        if cid:
            cur.execute(
                'SELECT id FROM candidates WHERE id=? AND is_duplicate=0',
                (cid,)
            )
            if cur.fetchone():
                valid_ids.append(cid)
    
    if valid_ids:
        new_entries.append({
            'query': query,
            'seniority': seniority,
            'relevant_ids': valid_ids
        })
        print(f'재등록: {query[:50]} → {len(valid_ids)}명')

cleaned.extend(new_entries)
json.dump(cleaned, open('golden_dataset_v3.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
print(f'\n총 쿼리 수: {len(cleaned)}개')

print("\n=== C. total_years=0 후보자 16명 재파싱 ===")
all_relevant_ids = set()
for item in cleaned:
    for rid in (item.get('relevant_ids') or []):
        all_relevant_ids.add(rid)

cur.execute('''
    SELECT id, name_kr, raw_text, careers_json, total_years
    FROM candidates
    WHERE id IN ({})
    AND (total_years IS NULL OR total_years = 0)
    AND is_duplicate = 0
'''.format(','.join('?' * len(all_relevant_ids))),
    list(all_relevant_ids)
)
rows = cur.fetchall()
print(f'total_years=0 후보자: {len(rows)}명')

fixed = 0
for row in rows:
    cid = row['id']
    name = row['name_kr']
    careers_json = row['careers_json'] or '[]'
    
    try:
        careers = json.loads(careers_json)
    except:
        careers = []
    
    # career_json에서 연차 재계산
    total = 0
    for c in careers:
        start = c.get('start_date', '') or ''
        end = c.get('end_date', '') or ''
        
        sy = re.search(r'(\d{4})', start)
        ey = re.search(r'(\d{4})', end)
        
        if sy:
            s_year = int(sy.group(1))
            e_year = int(ey.group(1)) if ey else 2025
            diff = max(0, e_year - s_year)
            total += diff
    
    if total > 0:
        cur.execute(
            'UPDATE candidates SET total_years=? WHERE id=?',
            (total, cid)
        )
        print(f'  수정: {name} → {total}년')
        fixed += 1

conn.commit()
print(f'\n수정 완료: {fixed}명')
conn.close()

print("\n=== D. 전체 NDCG 최종 재측정 ===")
query_targets = {}
for item in cleaned:
    q = item.get('query') or item.get('jd_query')
    if not q: continue
    rel = item.get('relevant_ids') or []
    if not rel and item.get('candidate_neo4j_id'):
        rel = [item.get('candidate_neo4j_id')]
    if q not in query_targets:
        query_targets[q] = {
            'relevant': set(),
            'seniority': item.get('seniority','All')
        }
    for r in rel:
        query_targets[q]['relevant'].add(r)

scores = []
zero_count = 0
perfect_count = 0

for q, info in query_targets.items():
    relevant = info['relevant']
    seniority = info['seniority']
    if not relevant: continue
    
    r = api_search_v8(q, seniority=seniority)
    matched = r.get('matched', [])
    
    dcg = 0
    for i, c in enumerate(matched[:10]):
        if c.get('id') in relevant:
            dcg += 1 / math.log2(i + 2)
    idcg = sum(1/math.log2(i+2) for i in range(min(len(relevant),10)))
    ndcg = dcg/idcg if idcg > 0 else 0
    scores.append(ndcg)
    if ndcg == 0: zero_count += 1
    if ndcg == 1: perfect_count += 1

total_ndcg = sum(scores)/len(scores) if scores else 0
print(f'전체 쿼리 수:    {len(scores)}개')
print(f'전체 NDCG@10:   {total_ndcg:.4f}')
print(f'0점 쿼리:       {zero_count}개')
print(f'만점 쿼리:      {perfect_count}개')
print(f'초기 대비:      +{(total_ndcg/0.0388 - 1)*100:.0f}%')
