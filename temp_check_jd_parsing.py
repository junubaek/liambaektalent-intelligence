
import sys
import os

# Root directory check
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT_DIR)
sys.stdout.reconfigure(encoding='utf-8')

from jd_compiler import parse_jd_to_json

def check_jd_parsing():
    q = 'Treasury_Management Cash_Flow_Management Corporate_Finance Financial_Management'
    result = parse_jd_to_json(q)
    conds = result.get('conditions', [])
    print(f'추출된 조건 수: {len(conds)}')
    for c in conds:
        print(f'  {c.get("skill")} (source: {c.get("source", "?")})')

if __name__ == "__main__":
    check_jd_parsing()
