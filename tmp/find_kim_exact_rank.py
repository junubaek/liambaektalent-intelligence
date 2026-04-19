import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from jd_compiler import parse_jd_to_json, get_embedding, prefilter_candidates, execute_search
import sqlite3

query = "6년차 이상 자금 담당자"
print(f"=== [쿼리] {query} ===")

jd_json = parse_jd_to_json(query)
jd_embedding = get_embedding(query)

df = prefilter_candidates(query, jd_json)
candidates_info = df.to_dict(orient='records')
top_300 = candidates_info[:300]

results = execute_search(jd_json, top_300, jd_embedding, limit=300)

found_rank = -1
for idx, c in enumerate(results):
    name = c.get('name_kr', c.get('name', ''))
    score = c['total_score']
    if idx < 5:
        print(f"[{idx+1}위] {name} | Score: {score}")
    if "김대중" in name:
        found_rank = idx + 1
        print(f"  👉 김대중님 (현재 {found_rank}위) | Score: {score}")
        print(f"     매칭 엣지들: {c.get('matched_raw', [])}")
        print(f"     모든 엣지들: {c.get('candidate_edges', [])}")
        
if found_rank == -1:
    print("김대중님이 300위 밖이거나 검색되지 않았습니다.")
