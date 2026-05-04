
import sys
import os

sys.stdout.reconfigure(encoding='utf-8')

from jd_compiler import api_search_v9

queries = [
    ('Driver_Development Embedded_Linux', ['정예린', '정윤오', '이신형']),
    ('VPP HVDC', ['배문성']),
    ('Treasury_Management Cash_Flow_Management Corporate_Finance Financial_Management', ['김대중']),
]

def run_checks():
    for q, targets in queries:
        r = api_search_v9(q)
        matched = r.get('matched', [])
        print(f'\n[{q[:40]}]')
        for i, c in enumerate(matched[:5]):
            name = c.get('name_kr','')
            marker = ' ←' if name in targets else ''
            print(f'  {i+1}. {name}{marker}')
        
        found = False
        for i, c in enumerate(matched):
            if c.get('name_kr') in targets:
                print(f'  → {c.get("name_kr")} 순위: {i+1}위')
                found = True
                break 
        if not found:
            print("  → Targets not found in results.")

if __name__ == "__main__":
    run_checks()
