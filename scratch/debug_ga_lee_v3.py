import sys, os
sys.stdout.reconfigure(encoding='utf-8')
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT_DIR)
os.chdir(ROOT_DIR)

from jd_compiler import api_search_v9

res = api_search_v9("General Affairs Manager")
target_id = 'db752f0f-0f1a-437c-a09d-43c20442ab7b'

print("--- GA Search Debug ---")
# Since api_search_v9 returns top 50, I'll search for him in the matched list
found = False
for i, cand in enumerate(res.get('matched', [])):
    if cand.get('id') == target_id:
        print(f"Found {cand.get('name_kr')} at rank {i+1}")
        print(f"  Score: {cand.get('final_score')}")
        print(f"  V: {cand.get('v_score')}, G: {cand.get('g_score')}, B: {cand.get('bm_score')}, D: {cand.get('depth_score')}")
        found = True
        break

if not found:
    print(f"Candidate {target_id} not found in Top 50.")
    # Let's check why. I'll print the scores of the Top 5 for comparison.
    print("\n--- Top 5 Candidates ---")
    for i, cand in enumerate(res.get('matched', [])[:5]):
        print(f"{i+1}. {cand.get('name_kr')} ({cand.get('id')[:8]})")
        print(f"   Score: {cand.get('final_score')} (V:{cand.get('v_score')} G:{cand.get('g_score')} B:{cand.get('bm_score')} D:{cand.get('depth_score')})")
