
import json
from jd_compiler import api_search_v9

q = "Blockchain NFT"
relevant = [
      "31f22567-1b6f-81f3-bfe6-fb7fd7c9ad61",
      "31f22567-1b6f-8150-8062-f6862dec66e5",
      "32022567-1b6f-8121-b3b4-dac79d7ece90",
      "32e22567-1b6f-81c5-8f9e-c02433e25876"
]

res = api_search_v9(q, seniority='All')
matched = res.get('matched', [])

print(f"Query: {q}")
print(f"Relevant IDs: {relevant}")
print("\nTop 10 Results:")
for i, c in enumerate(matched[:10]):
    cid = c.get('id')
    name = c.get('name_kr')
    score = c.get('final_score')
    v = c.get('v_score')
    g = c.get('g_score')
    b = c.get('bm_score')
    is_rel = str(cid) in relevant or str(c.get('candidate_id')) in relevant or name in relevant
    rel_marker = "[RELEVANT]" if is_rel else ""
    print(f"{i+1}. ID: {cid}, Name: {name}, Score: {score} (V:{v}, G:{g}, B:{b}) {rel_marker}")
