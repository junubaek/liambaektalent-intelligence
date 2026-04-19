from neo4j import GraphDatabase

def main():
    driver = GraphDatabase.driver('bolt://localhost:7687', auth=('neo4j', 'toss1234'))
    with driver.session() as session:
        # Check overall stats
        res = session.run("MATCH (c:Candidate) RETURN c.seniority as s, count(c) as cnt")
        print("=== OVERALL STATS ===")
        for record in res:
            print(f"{record['s']}: {record['cnt']}")
            
        print("\n=== KWAK CHANG-SHIN EDGES ===")
        res2 = session.run("MATCH (c:Candidate)-[r]->(s:Skill) WHERE c.name CONTAINS '곽창신' RETURN type(r) as action, s.name as skill ORDER BY s.name")
        for r2 in res2:
            print(f"{r2['action']}:{r2['skill']}")

if __name__ == "__main__":
    main()
