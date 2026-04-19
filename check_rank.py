import sys
import os

try:
    from backend.search_engine_v8 import api_search_v8
except ImportError:
    from jd_compiler import api_search_v8

def main():
    print("Testing Kubernetes OpenStack Terraform...")
    res = api_search_v8('Kubernetes OpenStack Terraform')
    matched = res.get('matched', []) if isinstance(res, dict) else res
    
    print('\n[Top-10 Candidates]')
    for i, c in enumerate(matched[:10], 1):
        print(f"{i}. {c.get('name')}")
        
    hit = next((i for i, c in enumerate(matched, 1) if c.get('name') == '최호진'), -1)
    print(f"\n=> 최호진 rank: {hit}")

if __name__ == '__main__':
    main()
