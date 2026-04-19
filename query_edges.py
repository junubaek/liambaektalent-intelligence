from neo4j import GraphDatabase

URI = "bolt://localhost:7687"
USER = "neo4j"
PASSWORD = "toss1234"

def run_query():
    print("Connecting to Neo4j to run aggregation query...")
    try:
        with GraphDatabase.driver(URI, auth=(USER, PASSWORD)) as driver:
            with driver.session() as session:
                query = """
                MATCH (c:Candidate)-[r]->(s:Skill)
                WHERE type(r) <> "HAS_SKILL"
                RETURN type(r) as action, count(*) as cnt
                ORDER BY cnt DESC
                """
                result = session.run(query)
                records = list(result)
                if not records:
                    print("No non-HAS_SKILL edges found! The DB might be empty or the parser failed.")
                else:
                    print("\n=== LLM Extracted Edges ===")
                    for record in records:
                        print(f"{record['action']:<15} | {record['cnt']} edges")
                    print("===========================\n")
    except Exception as e:
        print(f"Failed to connect or query Neo4j: {e}")

if __name__ == "__main__":
    run_query()
