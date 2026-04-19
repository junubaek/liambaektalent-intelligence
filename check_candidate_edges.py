from neo4j import GraphDatabase

uri = "neo4j://127.0.0.1:7687"
driver = GraphDatabase.driver(uri, auth=("neo4j", "toss1234"))

def check_candidate_edges():
    with driver.session() as session:
        cypher = """
        MATCH (c:Candidate)-[r]->(s:Skill)
        WHERE c.name CONTAINS '김대중' OR c.name CONTAINS '이범기'
        RETURN c.name as name, type(r) as action, s.name as skill
        """
        results = session.run(cypher)
        records = list(results)
        
        candidates = {}
        for r in records:
            name = r['name']
            if name not in candidates:
                candidates[name] = []
            candidates[name].append(f"{r['action']}:{r['skill']}")
            
        for name, edges in candidates.items():
            print(f"Candidate: {name}")
            print("Edges:")
            for e in edges:
                print(f"  {e}")
            print("-" * 20)
            
if __name__ == "__main__":
    check_candidate_edges()
