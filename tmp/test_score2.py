import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.stdout.reconfigure(encoding='utf-8')

import jd_compiler

print("--- Testing opt_match_score for Kim Dae-jung ONLY ---")
try:
    conds = [
      {
        "action": "MANAGED",
        "skill": "Treasury_Management",
        "weight": 1.0,
        "is_mandatory": True,
        "source": "native_dict"
      }
    ]
    names = ["김대중"]
    results = jd_compiler.opt_match_score(names, conds, min_years=0)
    
    print(f"Results returned: {len(results)}")
    for r in results:
        print(f"Name: {r.get('name')}, total_score: {r.get('total_score')}, Edges: {r.get('matched_edges')}")
        
except Exception as e:
    import traceback
    traceback.print_exc()
