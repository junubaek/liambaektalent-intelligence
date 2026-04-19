import os
import json
from app.engine.neo4j_snapper import Neo4jCandidateSnapper
from app.engine.resume_snap import CandidateSnapper

def main():
    uri = "neo4j+ssc://2c78ff2f.databases.neo4j.io"
    user = "neo4j"
    password = "sUdocj6IJEdIWCPNE6qzJq7kCdynS6EjSuBeKJtcye4"
    
    neo_engine = Neo4jCandidateSnapper(uri, user, password)
    
    # JD_6: B2B 반도체 테크 세일즈 리더
    jd_desc = "B2B 반도체 영업, 해외 영업, 전략 수립, 기술 영업 리딩"
    
    # 1. 텐던시 세팅 (Python 파서 의존)
    # 임시로 수동 세팅
    jd_tendency = {
        "Sales": 0.65,
        "Domain": 0.20, # Category mapped to Tech practically
        "Tech": 0.20, 
        "Business": 0.15,
        "Product": 0.0
    }
    
    # 2. JD Nodes 세팅 (가상 항성)
    jd_nodes_list = [
        {"name": "반도체", "weight": 5.0, "is_core": True},
        {"name": "영업", "weight": 2.0, "is_core": False},
        {"name": "B2B", "weight": 2.0, "is_core": False},
        {"name": "해외 영업", "weight": 2.0, "is_core": False},
        {"name": "전략_경영기획", "weight": 1.0, "is_core": False},
        {"name": "기술영업", "weight": 2.0, "is_core": False}
    ]
    
    print("🚀 Running Neo4j Cypher Gravity Engine for JD_6...")
    results = neo_engine.search_candidates(jd_tendency, jd_nodes_list)
    
    print("\n[🎯 Top 5 Candidates via Neo4j]")
    for i, r in enumerate(results[:5]):
        print(f"{i+1}위: {r['name']} (Score: {r['final_score']:.2f})")
        print(f"   [세부] Gravity: {r['raw_gravity']:.2f} | Tendency: {r['tendency_score']:.2f}")
        print(f"   [Sectors] {r.get('sectors')}")
        print("-" * 40)
        
    neo_engine.close()

if __name__ == "__main__":
    main()
