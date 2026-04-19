import sys
import os
import asyncio

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.stdout.reconfigure(encoding='utf-8')

import jd_compiler

print("--- Calling api_search_v8 ---")
try:
    # api_search_v8 might not be async! Oh wait, in line 923 it says `def api_search_v8`.
    # Let's check if it is async or sync.
    import inspect
    if inspect.iscoroutinefunction(jd_compiler.api_search_v8):
        res = asyncio.run(jd_compiler.api_search_v8("6년차 이상 자금 담당자"))
    else:
        res = jd_compiler.api_search_v8("6년차 이상 자금 담당자")
        
    # res might be a dict containing "matched"
    if isinstance(res, dict):
        candidates = res.get("matched", [])
    else:
        candidates = []
        
    print(f"Total Candidates Returned: {len(candidates)}")
    print("\n--- 1. Top 5 Candidates ---")
    for i, c in enumerate(candidates[:5]):
        print(f"[{i+1}] {c.get('이름', 'Unknown')} | Graph/Total Score: {c.get('_score', 0)} | Vector: {c.get('_vector_score', 0) if '_vector_score' in c else c.get('pinecone_score', 0)} | Final: {c.get('total_score', c.get('_score'))} | Max: {c.get('_max_score', 0)}")
        
    print("\n--- 2. 김대중님 점수 비교 ---")
    kim = next((c for c in candidates if '김대중' in c.get('이름', '')), None)
    if kim:
        idx = candidates.index(kim) + 1
        print(f"Name: {kim.get('이름')} | Rank: {idx}")
        print(f"Graph Score: {kim.get('_score', 0)}")
        print(f"Vector Score: {kim.get('pinecone_score', 0)}")
        print(f"Final Score: {kim.get('_score', 0)}")
        print(f"Max Score (Node 분모): {kim.get('_max_score', 0)}")
        print(f"Mechanics: {kim.get('_mechanics')}")
    else:
        print("김대중 NOT FOUND in the matched results!")

except Exception as e:
    print(f"Error: {e}")
