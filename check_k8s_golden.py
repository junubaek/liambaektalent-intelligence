import json
import sys
sys.stdout.reconfigure(encoding='utf-8')

# 1. Load the golden dataset
try:
    with open('golden_dataset_v3.json', 'r', encoding='utf-8') as f:
        golden_data = json.load(f)
except Exception as e:
    print(f"Error loading golden dataset: {e}")
    sys.exit(1)

# Group by jd_query
queries = {}
for item in golden_data:
    q = item.get('jd_query', '')
    if q not in queries:
        queries[q] = []
    if item.get('label') == 'positive':
        queries[q].append(item.get('candidate_name', ''))

# Target queries
target_queries = [q for q in queries.keys() if 'kubernetes' in q.lower() or 'devops' in q.lower() or 'vllm' in q.lower()]

if not target_queries:
    print("Cannot find such queries.")
    sys.exit(0)

# Import API
from jd_compiler import api_search_v8

for q in target_queries:
    positives = list(set(queries[q]))
    print(f"\n======================================")
    print(f"[Query]: {q}")
    print(f"======================================")
    print(f"Golden Positives ({len(positives)}명): {positives}")
    
    if '이준호' in positives:
        print("=> 💡 분석: 이준호는 이미 정답지(Positive)에 **포함**되어 있었습니다!")
    else:
        print("=> 💡 분석: 이준호는 정답지(Positive)에 **없었습니다** (새로 발굴된 실력자 이론 증명 가능성).")
        
    print("\n--- Current API Search Top 10 ---")
    try:
        res = api_search_v8(q)
        top_cands = res.get('matched', [])[:10]
        top_names = [c.get('name_kr', c.get('name', 'Unknown')) for c in top_cands]
        
        for i, c in enumerate(top_cands):
            name = c.get('name_kr', c.get('name', 'Unknown'))
            score = c.get('score', 0.0)
            mark = "✅(정답)" if name in positives else "❌(Miss)"
            print(f"  {i+1}. {name} (Score: {score:.2f}) {mark}")
            
        missed = [p for p in positives if p not in top_names]
        if missed:
            print(f"\n⚠️ Top 10에 진입하지 못한 정답자들: {missed}")
            all_cands = res.get('matched', [])
            all_names = [c.get('name_kr', c.get('name', 'Unknown')) for c in all_cands]
            for m in missed:
                if m in all_names:
                    rank = all_names.index(m) + 1
                    print(f" - {m}: 현재 {rank}위 (Score: {all_cands[rank-1].get('score', 0):.2f})")
                else:
                    print(f" - {m}: 전체 검색 결과(1순위 필터링)에 아예 잡히지 않음!")
    except Exception as e:
        print(f"Search error: {e}")
