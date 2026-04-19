import os
import json
import logging

from jd_compiler import api_search_v8

def run_tests():
    logging.basicConfig(level=logging.INFO)
    
    # Test 1
    print("\n\n" + "="*50)
    print("TEST 1: vLLM PyTorch llm serving")
    res1 = api_search_v8('vLLM PyTorch llm serving')
    for i, c in enumerate(res1.get('matched', [])[:10]):
        print(f"[{i+1}] {c['name_kr']} - Score: {c['score']} / Edges: {c.get('total_edges')}")

    # Test 2
    print("\n\n" + "="*50)
    print("TEST 2: kubernetes devops")
    res2 = api_search_v8('kubernetes devops')
    for i, c in enumerate(res2.get('matched', [])[:10]):
        print(f"[{i+1}] {c['name_kr']} - Score: {c['score']} / Edges: {c.get('total_edges')}")

    # Test 3
    print("\n\n" + "="*50)
    print("TEST 3: 연결회계")
    res3 = api_search_v8('연결회계')
    for i, c in enumerate(res3.get('matched', [])[:10]):
        print(f"[{i+1}] {c['name_kr']} - Score: {c['score']} / Edges: {c.get('total_edges')}")
        
    # Manual check for Oh Won-gyo Terraform
    print("\n\n" + "="*50)
    print("TEST 4: Terraform SQLite Fallback check for 오원교")
    res4 = api_search_v8('Terraform')
    for i, c in enumerate(res4.get('matched', [])):
        if c['name_kr'] == '오원교':
            print(f"✅ 오원교 found at rank {i+1} with score {c['score']} / Edges: {c.get('total_edges')}")
            break
    else:
        print("❌ 오원교 NOT found in Terraform query!")

if __name__ == '__main__':
    run_tests()
