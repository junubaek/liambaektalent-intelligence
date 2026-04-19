import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.stdout.reconfigure(encoding='utf-8')

import jd_compiler

print("--- Calling api_search_v8 ---")
try:
    # 6년차 이상 자금 담당자
    res = jd_compiler.api_search_v8("6년차 이상 자금 담당자")
    
    candidates = res.get("matched", res.get("candidates", []))
    
    print(f"\nTotal Candidates Returned: {len(candidates)}")
    print("\n--- 1. Top 5 Candidates ---")
    for i, c in enumerate(candidates[:5]):
        print(f"[{i+1}] {c.get('이름', 'Unknown')} | Graph Score: {c.get('_score', 0)} | Vector: {c.get('pinecone_score', 0)} | Final: {c.get('total_score', c.get('_score'))} | Max: {c.get('_max_score', 0)}")
        
    print("\n--- 2. 김대중님 위치/점수 비교 ---")
    kim = next((c for c in candidates if '김대중' in c.get('이름', '')), None)
    if kim:
        idx = candidates.index(kim) + 1
        print(f"Name: {kim.get('이름')} | Rank: {idx}")
        print(f"Graph Score: {kim.get('_score', 0)}")
        print(f"Vector Score: {kim.get('pinecone_score', 0)}")
        print(f"Final Score: {kim.get('total_score', kim.get('_score'))}")
        print(f"Max Score (Node 분모): {kim.get('_max_score', 0)}")
        print(f"Mechanics: {kim.get('_mechanics')}")
    else:
        print("김대중 NOT FOUND in the API matched results!")
        # Let's check why: check if min_years is the culprit in Neo4j graph for Kim Dae-jung.
        from neo4j import GraphDatabase
        uri = "bolt://127.0.0.1:7687"
        driver = GraphDatabase.driver(uri, auth=("neo4j", "toss1234"))
        with driver.session() as session:
            result = session.run("MATCH (c:Candidate {name_kr: '김대중'}) RETURN c.total_years as ty")
            rec = next(iter(result), None)
            print(f"Neo4j record for 김대중 total_years: {rec['ty'] if rec else 'No Node'}")

except Exception as e:
    import traceback
    traceback.print_exc()

print("\nDone.")
