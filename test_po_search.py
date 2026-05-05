import sys
sys.stdout.reconfigure(encoding='utf-8')
from jd_compiler import search_candidates

results = search_candidates(
    prompt='Product Owner 찾아줘',
    sectors=[],
    seniority=['All'],
    required=[],
    preferred=[]
)

print("=== Search Results: Product Owner ===")
for i, r in enumerate(results[:15]):
    name = r.get('이름') or r.get('name_kr', '?')
    score = r.get('final_score', 0)
    g = r.get('graph_score', 0)
    v = r.get('vector_score', 0)
    company = r.get('current_company', '?')
    print(f"{i+1}. {name} | {company} | FINAL: {score:.4f} G: {g:.4f} V: {v:.4f}")
