import asyncio
import sys
import os

sys.path.append(os.getcwd())
from backend.search_engine_v5 import search_candidates

def main():
    print("Running diagnostic search through search_engine_v5...")
    result = search_candidates(
        prompt="IPO 대비 PR 경력자",
        sectors=["마케팅 (Marketing)"],
        seniority="Senior",
        required=["PR"],
        preferred=["인하우스"]
    )
    
    print(f"\nTotal Returned: {result.get('total', 0)}")
    print(f"Matched: {len(result.get('matched', []))}")
    print(f"Nearby: {len(result.get('nearby', []))}")
    print(f"Alternative: {result.get('alternative', {}).get('type')}")
    
    if result.get('matched'):
        print("\n--- SAMPLE MATCHED CANDIDATE ---")
        print(result['matched'][0]['Name'])

if __name__ == "__main__":
    main()
