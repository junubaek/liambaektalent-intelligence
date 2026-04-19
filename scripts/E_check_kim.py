from neo4j import GraphDatabase

def main():
    driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "password"))
    with driver.session() as session:
        res = session.run("MATCH (c:Candidate) WHERE c.name_kr='김대중' RETURN c.id, c.is_duplicate, c.summary").data()
        print("Neo4j 김대중 Nodes:")
        for r in res:
            print(r)
            
if __name__ == "__main__":
    main()
