import sys
import logging
import json
sys.stdout.reconfigure(line_buffering=True)
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

sys.path.append('C:/Users/cazam/Downloads/이력서자동분석검색시스템')
import jd_compiler

print("\n=======================================================")
print('하이브리드 검색 E2E 시뮬레이션')
print("=======================================================\n")

queries = ["IR 담당자 6년차", "리텐션 마케터"]

for q in queries:
    print(f"\n검색 쿼리: '{q}'")
    print("-" * 50)
    
    # Run the V8 search API
    res = jd_compiler.api_search_v8(q)
    
    # 1. Parsing & Routing Trace
    parsed_req = res.get('parsed_request', {})
    print("[1. JD 컴파일러 파싱 결과]")
    print(f" - 추출된 노드(L1): {parsed_req.get('extracted_nodes_l1')}")
    print(f" - 대체 벡터노드(L2) / Pinecone: {parsed_req.get('fallback_vector_nodes', '내부 처리됨')}")
    print(f" - 선호 연차(Seniority): {parsed_req.get('original_seniority', 'N/A')}")
    
    # 2. Result Dump
    results = res.get('results', [])
    print(f"\n[2. 최종 랭킹 결과 (상위 3명)] - 총 {res.get('total', 0)}명 검색됨")
    
    for i, p in enumerate(results[:3]):
        # Extract Score info
        gravity = p.get('scoreInfo', {}).get('Graph Gravity', 0)
        vector_s = p.get('scoreInfo', {}).get('Vector Harmony', 0)
        fusion = p.get('combinedScore', 0)
        
        name = p.get('name', '미상')
        company = p.get('company', '미상')
        exp = p.get('totalExperience', p.get('total_exp', 0))
        
        print(f"  {i+1}위: {name} ({company}, {exp}년차)")
        print(f"      => Fusion Score: {fusion:.4f} [Graph: {gravity:.2f} + Vector: {vector_s:.4f}]")
    print("\n" + "="*55)
