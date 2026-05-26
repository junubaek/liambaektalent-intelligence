import sys, os, math
sys.stdout.reconfigure(encoding='utf-8')
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT_DIR)
os.chdir(ROOT_DIR)

from jd_compiler import api_search_v9

target_id = 'db752f0f-0f1a-437c-a09d-43c20442ab7b'
res = api_search_v9("General Affairs Manager")

# api_search_v9 sorts and slices to 50. 
# I want to find his score even if he is at rank 100.
# I'll look into the 'matched' list first.

found = False
for i, cand in enumerate(res.get('matched', [])):
    if cand.get('id') == target_id:
        print(f"Found at rank {i+1}")
        print(f"Score: {cand.get('final_score')}")
        found = True
        break

if not found:
    print("Not in top 50.")
    # I'll check if he is in the combined pool by calculating his score manually
    # But wait, api_search_v9 uses Neo4j vector search to get top 100.
    # If he is not in Neo4j's top 100 vectors, he might not even be in the combined pool!
