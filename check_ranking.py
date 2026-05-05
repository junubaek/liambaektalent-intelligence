import sys
import json
from jd_compiler import api_search_v9

sys.stdout.reconfigure(encoding='utf-8')

query = "senior cfo"
res = api_search_v9(query)
matched = res.get('matched', [])

print(f"Total matched: {len(matched)}")
found = False
for i, c in enumerate(matched):
    name = c.get('name_kr', 'Unknown')
    company = c.get('current_company', 'None')
    score = c.get('hybrid_score', 0)
    print(f"Rank {i+1}: {name} ({company}) - Score: {score}")
    if name == "김은형":
        print(f"*** FOUND 김은형 AT RANK {i+1} ***")
        print(f"Debug Info: {c.get('debug_score')}")
        found = True

if not found:
    print("김은형 was not found in the top results.")
