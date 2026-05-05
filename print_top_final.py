import sys
from jd_compiler import api_search_v9

sys.stdout.reconfigure(encoding='utf-8')

res = api_search_v9("senior cfo")
matched = res.get('matched', [])

print(f"Total matched: {len(matched)}")
for i, c in enumerate(matched[:50]):
    name = c.get('name_kr')
    cid = c.get('id')
    score = c.get('final_score')
    print(f"Rank {i+1}: {name} ({cid}) - Score: {score}")
