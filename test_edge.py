from neo4j import GraphDatabase

URI = "bolt://localhost:7687"
USER = "neo4j"
PASSWORD = "toss1234"

def run_query():
    try:
        with GraphDatabase.driver(URI, auth=(USER, PASSWORD)) as driver:
            with driver.session() as session:
                query = """
                MATCH (c:Candidate)-[r]->(s:Skill)
                WHERE c.name CONTAINS '박성준'
                AND type(r) <> 'HAS_SKILL'
                RETURN c.name as c_name, type(r) as r_type, s.name as s_name
                """
                result = session.run(query)
                records = list(result)
                if not records:
                    print("No edges found for 박성준. Result is empty.")
                else:
                    for record in records:
                        print(f"[{record['c_name']}] -[{record['r_type']}]-> [{record['s_name']}]")
    except Exception as e:
        print(f"Failed to connect or query Neo4j: {e}")

if __name__ == "__main__":
    run_query()
