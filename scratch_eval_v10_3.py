import asyncio
import json
from jd_compiler import api_search_v10

async def test_v10_3_precision():
    queries = [
        "Kubernetes 기반의 MLOps 플랫폼을 구축하고, Kafka를 활용해 대규모 데이터 파이프라인을 설계한 경험 (김영인 타겟)",
        "경영전략을 수립하고 자금 운용(Treasury) 및 외환 관리를 총괄하며, ERP 시스템을 구축해본 재무 전문가 (김대중 타겟)",
        "Python 기반의 데이터 엔지니어링 및 백엔드 개발, SAP 시스템 연동과 정보보안 체계를 구축해본 경험 (김완희 타겟)"
    ]
    
    target_names = ["김영인", "김대중", "김완희"]
    
    print("=== v10.3 Bayesian Hybrid Engine Evaluation ===")
    
    for i, q in enumerate(queries):
        print(f"\nQuery: {q}")
        results = await api_search_v10({"query": q, "top_k": 5})
        
        found_target = False
        for idx, res in enumerate(results):
            print(f"{idx+1}. {res['name']} (Score: {res['score']}) - L1:{res['layers']['ontology']:.2f}, L2:{res['layers']['bayesian']:.2f}, L3:{res['layers']['semantic']:.2f}")
            if target_names[i] in res['name']:
                print(f"FOUND {target_names[i]} at Rank {idx+1}")
                found_target = True
        
        if not found_target:
            print(f"FAILED to find {target_names[i]} in Top 5")

if __name__ == "__main__":
    asyncio.run(test_v10_3_precision())
