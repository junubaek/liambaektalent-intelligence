import sys
import json
from jd_compiler import api_search_v9

# Ensure UTF-8 output
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

prompt = 'Enterprise Sales Manager'
target_id = 'c3d4ee55-266a-44f6-8e66-fb7486be38a8'
target_name = '최우성'

res = api_search_v9(prompt=prompt, seniority='All')
candidates = res.get('matched', [])

print(f"Target Search: '{prompt}'")
print(f"Expected Target: {target_name} ({target_id})")
print("-" * 50)

found = False
for i, c in enumerate(candidates[:30]):
    cid = str(c.get('id', ''))
    name = c.get('name_kr', '')
    is_match = (cid == target_id)
    if is_match: found = True
    print(f"Rank {i+1:2d}: {name:10s} | ID: {cid} | Match: {is_match}")

if not found:
    print("\nTarget NOT FOUND in Top 30.")
    # Search deeper
    for i, c in enumerate(candidates[30:]):
        if str(c.get('id')) == target_id:
            print(f"Found {target_name} at Rank {i+31}")
            found = True
            break

if not found:
    print("Target NOT FOUND in entire search pool.")
