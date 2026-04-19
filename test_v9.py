import time
from jd_compiler import api_search_v9

st = time.time()
print('Testing V8.9 Native Neo4j Engine (K8s 인프라 자동화 구축)...')
results = api_search_v9('K8s 인프라 자동화 구축', 'debug_sid_01')

for idx, r in enumerate(results[:3]):
    name = r.get("name", "")
    hsh = r.get("hash", "")
    g_sc = r.get("graph_score", 0.0)
    v_sc = r.get("vector_score", 0.0)
    print(f"{idx+1}. {name} ({hsh}) | Graph: {g_sc:.2f} | Vector: {v_sc:.2f}")

print(f"Total retrieved: {len(results)}")
print(f"Time: {time.time()-st:.2f}s")
