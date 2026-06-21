import sqlite3
import json
import sys
import math

sys.stdout.reconfigure(encoding='utf-8')

with open('secrets.json', encoding='utf-8') as f:
    secrets = json.load(f)

# Connect to SQLite
conn = sqlite3.connect('candidates.db')
cur = conn.cursor()

tests = [
    ('SCM logistics operations cost management', 'MIDDLE', '31f22567-1b6f-8152-93ca-ca5ab3080016', '유정한'),
    ('on-device AI inference embedded AI semiconductor', 'SENIOR', 'ba4abc09-302e-4fd4-ae93-b8af52aed567', '하현재'),
    ('healthcare AI computer vision deep learning medical imaging', 'MIDDLE', '32022567-1b6f-819f-b62e-fa5ecb02e3de', '김진영'),
    ('IPO IR strategic planning fundraising finance', 'SENIOR', '1c3e3279-b0c5-4661-9dcf-7fa929dd47bb', '김진호'),
]

# We will run a script that imports jd_compiler and patches the result limit temporarily or traces the candidate directly.
# Wait, let's inspect jd_compiler.py's return statement in api_search_v9:
# It returns a dict with "matched": final_candidates[:50].
# Let's inspect where final_candidates is computed and see if we can run the logic.
# Or we can just read the first 100 ranks! Let's write a script that runs the search but prints ranks up to 300!
# Wait! How can we print ranks up to 300 if api_search_v9 only returns 50?
# We can temporarily edit api_search_v9 in jd_compiler.py to return final_candidates[:300] or write a wrapper that queries it.
# Let's write a python code that reads jd_compiler.py, replaces final_candidates[:50] with final_candidates[:300], runs our rank check, and then restores it!
# That is very clean and simple.

with open('jd_compiler.py', 'r', encoding='utf-8') as f:
    orig_code = f.read()

# Replace limit of 50 with 300
patched_code = orig_code.replace('final_candidates[:50]', 'final_candidates[:300]')
with open('jd_compiler.py', 'w', encoding='utf-8') as f:
    f.write(patched_code)

print("Temporarily patched jd_compiler.py to return top 300 matched candidates.")

try:
    from jd_compiler import api_search_v9
    
    for query, seniority, target_id, name in tests:
        r = api_search_v9(query, seniority=seniority)
        matched = r.get('matched', [])
        rank = next((i+1 for i, c in enumerate(matched) if c.get('id') == target_id), None)
        top1 = matched[0] if matched else {}
        print(f"[{name}] rank={rank} | 1위={top1.get('name_kr','?')} (score={top1.get('final_score',0):.3f}, g={top1.get('g_score',0):.3f}, v={top1.get('v_score',0):.3f})")
        
        # If found, print score breakdown
        if rank:
            c = matched[rank-1]
            print(f"  -> Target {name} score breakdown: final={c.get('final_score',0):.4f}, g_score={c.get('g_score',0):.3f}, v_score={c.get('v_score',0):.3f}")
finally:
    # Restore original code
    with open('jd_compiler.py', 'w', encoding='utf-8') as f:
        f.write(orig_code)
    print("Restored original jd_compiler.py.")
