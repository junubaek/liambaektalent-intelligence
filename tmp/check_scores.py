import sys
import os
import asyncio
import json

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.stdout.reconfigure(encoding='utf-8')

import jd_compiler

async def run_search():
    payload = {
        "jd_text": "6년차 이상 자금 담당자",
        "search_type": "deep"
    }
    # api_search_v8 expects a dict or Request? In jd_compiler, it's usually defined as:
    # async def api_search_v8(payload: dict)
    try:
        from pydantic import BaseModel
        class SearchPayload(BaseModel):
            jd_text: str
            search_type: str = "deep"
        
        req = SearchPayload(jd_text="6년차 이상 자금 담당자")
        res = await jd_compiler.api_search_v8(req)
        
        candidates = res.candidates
    except Exception:
        # If it's a dict
        try:
            res = await jd_compiler.api_search_v8({"jd_text": "6년차 이상 자금 담당자", "search_type": "deep"})
            if isinstance(res, dict): candidates = res.get("candidates", [])
            else: candidates = res.candidates
        except Exception as e:
            print(f"Error calling search: {e}")
            return
            
    # Show Top 5
    print("--- Top 5 Candidates ---")
    for i, c in enumerate(candidates[:5]):
        name = c.get("이름", "Unknown") if isinstance(c, dict) else ""
        if hasattr(c, "이름"): name = getattr(c, "이름")
        if isinstance(c, dict):
            cs = c.get("_score", 0)
            vs = c.get("_vector_score", 0)
            max_s = c.get("_max_score", 0)
            print(f"{i+1}. {name} | Final/Graph Score: {cs} | Vector: {vs} | Max: {max_s}")
        else:
            print(f"{i+1}. {name} | Final/Graph Score: {getattr(c, '_score', 0)} | Vector: {getattr(c, '_vector_score', 0)} | Max: {getattr(c, '_max_score', 0)}")
            
    # Show Kim Dae-jung
    print("\n--- Kim Dae-jung ---")
    kim = None
    if isinstance(candidates[0], dict):
        kim = next((c for c in candidates if '김대중' in c.get("이름", "")), None)
        if kim:
            print(f"Rank: {candidates.index(kim)+1} | Name: {kim.get('이름')} | Final: {kim.get('_score')} | Vector: {kim.get('_vector_score')} | Max: {kim.get('_max_score')}")
        else:
            print("김대중 NOT FOUND in results!")
    else:
        kim = next((c for c in candidates if hasattr(c, '이름') and '김대중' in getattr(c, '이름')), None)
        if kim:
            print(f"Rank: {candidates.index(kim)+1} | Name: {getattr(kim, '이름')} | Final: {getattr(kim, '_score')} | Vector: {getattr(kim, '_vector_score')} | Max: {getattr(kim, '_max_score')}")
        else:
            print("김대중 NOT FOUND in results!")

asyncio.run(run_search())
