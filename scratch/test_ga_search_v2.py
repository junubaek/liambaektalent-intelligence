import sys, os
sys.stdout.reconfigure(encoding='utf-8')
# Go up one level from scratch/
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT_DIR)
os.chdir(ROOT_DIR) # Change directory to root to find secrets.json etc.

from jd_compiler import api_search_v9

res = api_search_v9("General Affairs Manager")
matched = res.get('matched', [])
print("--- General Affairs Manager Search Results ---")
for i, cand in enumerate(matched[:10]):
    print(f"{i+1}. {cand.get('name_kr')} ({cand.get('id')})")
