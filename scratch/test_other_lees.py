import sys, os, json
sys.stdout.reconfigure(encoding='utf-8')
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT_DIR)
os.chdir(ROOT_DIR)

from jd_compiler import api_search_v9

test_cases = [
    {"query": "Overseas Sales Manager", "target_id": "898ea4e0-77d4-46d5-bf4d-c2d5b4a04741", "label": "Sales"},
    {"query": "Bioinformatics Engineer", "target_id": "55726c4a-4601-4ee9-87dc-581d15eda75e", "label": "Bio"}
]

for case in test_cases:
    print(f"--- Testing {case['label']} ({case['query']}) ---")
    res = api_search_v9(case['query'])
    matched = res.get('matched', [])
    found = False
    for i, cand in enumerate(matched[:20]):
        if cand.get('id') == case['target_id']:
            print(f"  ✅ Found at Rank {i+1} with score {cand.get('final_score')}")
            found = True
            break
    if not found:
        print(f"  ❌ Not found in Top 20.")
    print()
