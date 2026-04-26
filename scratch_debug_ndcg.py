
import json
from jd_compiler import api_search_v9

q = "Neural Network Operations Parallel Programming C++"
relevant = [
      "31f22567-1b6f-8106-a331-e438f877d966",
      "31f22567-1b6f-81e9-9eec-c735494cc02f",
      "31f22567-1b6f-814d-9e7b-cf300cd3447f",
      "32e22567-1b6f-81e7-b76e-ce60c2ccfaa7"
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
