import json
from neo4j import GraphDatabase

uri = "neo4j://127.0.0.1:7687"
driver = GraphDatabase.driver(uri, auth=("neo4j", "toss1234"))

def check_neo4j_node():
    with driver.session() as session:
        # Check exactly for "김완희"
        result = session.run("MATCH (c:Candidate) WHERE c.name CONTAINS '김완희' RETURN c.name, c.name_kr, c.phone, c.email")
        records = list(result)
        if records:
            for r in records:
                print(f"[Neo4j] Name: {r['c.name']}, Kr_Name: {r['c.name_kr']}, Phone: {r['c.phone']}, Email: {r['c.email']}")
        else:
            print("[Neo4j] No node found for 김완희.")

if __name__ == "__main__":
    check_neo4j_node()
    
    # Also test the jd_compiler
    import jd_compiler
    # Just force a small query that definitely hits
    print("\\n[JD Compiler Test]")
    jd_compiler.run_jd_compiler("정산 시스템 설계한 사람 찾아줘")

