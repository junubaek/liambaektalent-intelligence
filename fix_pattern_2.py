from neo4j import GraphDatabase

NEO4J_URI = "neo4j://127.0.0.1:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "toss1234"
driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

Q_REPLACE = """
MATCH (c)-[r:ANALYZE|ANALYED|ANALYSED]->(s)
MERGE (c)-[new_r:ANALYZED]->(s)
SET new_r = properties(r)
DELETE r
RETURN count(new_r) as changed
"""

def fix_edges():
    with driver.session() as session:
        res = session.run(Q_REPLACE)
        changed = res.single()["changed"]
        print(f"오타 엣지 수정 완료. 통일된 엣지 수: {changed}")

if __name__ == "__main__":
    fix_edges()
