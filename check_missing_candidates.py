from neo4j import GraphDatabase
import json
from jd_compiler import api_search_v8

def main():
    driver = GraphDatabase.driver('bolt://127.0.0.1:7687', auth=('neo4j', 'toss1234'))
    names = ['오원교', '유준상', '정윤오']
    
    with driver.session() as session:
        for name in names:
            res = session.run("MATCH (c:Candidate {name_kr: $name})-[r]->(s) RETURN type(r) AS rel, s.name AS skill", name=name)
            edges = [f"[{record['rel']}] -> {record['skill']}" for record in res]
            print(f"Edges for {name}: {len(edges)} total")
            for e in edges:
                print(f"  {e}")
            print("-" * 40)
            
    driver.close()
    
    print("\n[Search Top-10 for 'Kubernetes Terraform LangGraph']")
    search_res = api_search_v8('Kubernetes Terraform LangGraph')
    matched = search_res.get('matched', [])[:10]
    for i, m in enumerate(matched, 1):
        print(f"Rank {i}: {m['name']} (Score: {m['score']})")

if __name__ == '__main__':
    main()
