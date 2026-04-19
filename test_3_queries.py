import sys
import subprocess
sys.stdout.reconfigure(encoding='utf-8')
from jd_compiler import api_search_v8

tests = [
    'vLLM PyTorch',
    'kubernetes devops',
    '연결회계'
]

print("=== api_search_v8 Test ===\n")
for q in tests:
    print(f"[Query]: {q}")
    res = api_search_v8(q)
    results = res.get("matched", [])
    if not results:
        print("  None")
    for i, r in enumerate(results[:5]):
        print(f"  {i+1}. {r.get('name_kr', r.get('name', 'Unknown'))} (Score: {r.get('score', 0.0):.2f})")
    print("-" * 40)
        
print("\n=== NDCG Evaluation ===")
try:
    result = subprocess.run(["python", "run_real_evaluate_v3.py"], capture_output=True, encoding='utf-8', errors='ignore')
    print(result.stdout)
except Exception as e:
    print(e)
