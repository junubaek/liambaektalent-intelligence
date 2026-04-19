import sys
import json
sys.path.append('.')

from backend.search_engine_v6 import search_candidates_v6

prompt = '''토스에서 Financial System Manager를 뽑아.
PM, PO 라고 생각하면 되고, 정산/회계 쪽을 다뤄보신 분을 원해
개발쪽 경험이 짧게 있으면 좋고, 최소 6년 차 이상 경험자를 모시려고 해.

이 포지션은 재무회계 경력자를 뽑는게 아니라, 정산 데이터 라인을 구축하고 분석해서 설계하는 포지션이야.

말하자면 정산 System PM 인거지. 정산 시스템을 기획/구축해주실 분을 뽑는거야'''

try:
    res = search_candidates_v6(
        prompt=prompt,
        sectors=[],
        seniority="6년 이상",
        required=[],
        preferred=[]
    )
    
    print("MATCHED CANDIDATES:")
    for i, c in enumerate(res.get('matched', [])):
        print(f"{i+1}. {c['이름']} | Score: {c['_score']} | Mechanics: {c['_mechanics']}")
        print(f"   Sectors: {c['Main Sectors']} | Sub: {c['Sub Sectors']}")
        print(f"   Summary: {c['Experience Summary'][:100]}...\n")
        
    print("NEARBY CANDIDATES:")
    for i, c in enumerate(res.get('nearby', [])[:3]):
        print(f"{i+1}. {c['이름']} | Score: {c['_score']} | Mechanics: {c['_mechanics']}")
        
except Exception as e:
    print("Error:", e)
