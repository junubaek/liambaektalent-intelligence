import sys
sys.stdout.reconfigure(encoding='utf-8')

import jd_compiler

# Let's inspect the scoring for 'UIUX 디자이너' and 'General Affairs Manager'
queries_to_debug = [
    ('UIUX 디자이너', '이영도', '8e4b53e0-5f55-41d7-a311-c43d9727c516'),
    ('General Affairs Manager', '이상헌', 'db752f0f-0f1a-437c-a09d-43c20442ab7b')
]

for q, target_name, target_id in queries_to_debug:
    print(f"\n================ DEBUGGING: '{q}' (Target: {target_name}, ID: {target_id}) ================")
    try:
        res = jd_compiler.api_search_v9(prompt=q)
        matched = res.get("matched", [])
        
        # Check if target is in matched list
        found = False
        for rank, item in enumerate(matched, 1):
            name = item.get("name") or item.get("name_kr")
            if name == target_name or item.get("id") == target_id:
                print(f"🎯 Target found at rank {rank}!")
                print(f"  Item info: {item}")
                found = True
                break
        
        if not found:
            print("❌ Target not found in the full matched list!")
            
    except Exception as e:
        print(f"🚨 Error: {e}")
