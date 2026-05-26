import sys, os
sys.stdout.reconfigure(encoding='utf-8')
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT_DIR)
os.chdir(ROOT_DIR)

from jd_compiler import api_search_v9

res = api_search_v9("General Affairs Manager")
matched = res.get('matched', [])
target_id = 'db752f0f-0f1a-437c-a09d-43c20442ab7b'

print("--- GA Search Debug ---")
found = False
for i, cand in enumerate(matched):
    if cand.get('id') == target_id:
        print(f"Found Lee Sang-heon at rank {i+1} with score {cand.get('score', 'N/A')}")
        found = True
        break

if not found:
    print(f"Lee Sang-heon ({target_id}) not found in results.")
    # Check if he is in the cache or vector tower at all
    print(f"Total matched candidates: {len(matched)}")
