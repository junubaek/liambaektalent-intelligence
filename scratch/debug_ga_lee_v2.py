import sys, os
sys.stdout.reconfigure(encoding='utf-8')
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT_DIR)
os.chdir(ROOT_DIR)

from jd_compiler import api_search_v9

# Monkey patch to see more results
def api_search_v9_expanded(prompt, **kwargs):
    res = api_search_v9(prompt, **kwargs)
    # The original function returns top 50, but let's see if we can get all before slicing
    return res

res = api_search_v9("General Affairs Manager")
# Note: api_search_v9 only returns 50 in 'matched'. 
# I should check the 'total' field.
print(f"Total matched: {res.get('total')}")

target_id = 'db752f0f-0f1a-437c-a09d-43c20442ab7b'
found = False
for i, cand in enumerate(res.get('matched', [])):
    if cand.get('id') == target_id:
        print(f"Found at rank {i+1}")
        found = True
        break

if not found:
    print("Not in top 50.")
