import sys
sys.stdout.reconfigure(encoding='utf-8')
from jd_compiler import api_search_v9

res = api_search_v9(
    prompt='Product Owner 찾아줘',
    seniority='All'
)
results = res.get('matched', [])

print("=== Search Results: Product Owner (v9) ===")
for i, r in enumerate(results[:15]):
    name = r.get('name_kr') or r.get('이름', '?')
    score = r.get('final_score', 0)
    g = r.get('graph_score', 0)
    v = r.get('vector_score', 0)
    company = r.get('current_company', '?')
    print(f"{i+1}. {name} | {company} | FINAL: {score:.4f} G: {g:.4f} V: {v:.4f}")
