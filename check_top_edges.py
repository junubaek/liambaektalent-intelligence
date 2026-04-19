import sys
import json
sys.stdout.reconfigure(encoding='utf-8')
from neo4j import GraphDatabase

driver = GraphDatabase.driver("bolt://127.0.0.1:7687", auth=("neo4j", "toss1234"))

def check_top():
    with driver.session() as s:
        q = """
        MATCH (c:Candidate)-[r]->(s:Skill)
        WHERE r.source = 'llm_parsed_step6'
        WITH c, count(r) AS edge_count
        ORDER BY edge_count DESC
        LIMIT 3
        
        MATCH (c)-[r]->(s:Skill)
        WHERE r.source = 'llm_parsed_step6'
        RETURN c.name_kr AS name, edge_count, collect({action: type(r), skill: s.name}) AS edges
        ORDER BY edge_count DESC
        """
        results = s.run(q).data()
        for idx, res in enumerate(results):
            print(f"[{idx+1}] {res['name']} (총 엣지수: {res['edge_count']}개)")
            edges = res['edges']
            # Group by skill to see if there are too many verbs per skill
            grouped = {}
            for e in edges:
                sk = e['skill']
                act = e['action']
                grouped.setdefault(sk, []).append(act)
                
            for sk, acts in sorted(grouped.items()):
                print(f"  - {sk}: {', '.join(acts)}")
            print("-" * 50)

if __name__ == "__main__":
    check_top()
    driver.close()
