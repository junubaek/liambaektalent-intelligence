from neo4j import GraphDatabase

uri = "neo4j://127.0.0.1:7687"
driver = GraphDatabase.driver(uri, auth=("neo4j", "toss1234"))

def check_years():
    with driver.session() as session:
        cypher = "MATCH (c:Candidate) WHERE c.name CONTAINS '김대중' OR c.name CONTAINS '이범기' RETURN c.name as name, c.total_years as ys"
        results = session.run(cypher)
        for r in list(results):
            print(f"Name: {r['name']}, Years: {r['ys']}")
            
if __name__ == "__main__":
    check_years()
