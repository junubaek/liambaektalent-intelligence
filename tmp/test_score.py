import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.stdout.reconfigure(encoding='utf-8')

import jd_compiler

print("--- 1. Querying opt_match_score directly ---")
try:
    # Build a simulated condition based on what parse_jd_to_json parsed earlier
    conds = [
      {
        "action": "MANAGED",
        "skill": "Treasury_Management",
        "weight": 1.0,
        "is_mandatory": True,
        "source": "native_dict"
      }
    ]
    # We will get names of top 5 people in DB with Treasury Management, + Kim Dae-jung
    names = ["김대중", "강성우", "이승현", "박준석", "정민용"]
    
    results = jd_compiler.opt_match_score(names, conds, min_years=0)  # min_years 0 to avoid total_years filtering
    
    print(f"Results returned: {len(results)}")
    for r in results:
        print(f"Name: {r.get('name')}, total_score: {r.get('total_score')}, Edges: {r.get('matched_edges')}")
        
    print("\n--- max_score evaluation ---")
    base_max = sum(c.get("weight", 1.0) for c in conds)
    max_score = round(base_max + 1.5, 2) if base_max > 0 else 5.0
    print(f"Calculated max_score for UI: {max_score}")
    
except Exception as e:
    print(f"Error: {e}")
