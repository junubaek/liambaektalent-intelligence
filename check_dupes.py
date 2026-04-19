from neo4j import GraphDatabase

def check_dupes():
    uri = "neo4j://127.0.0.1:7687"
    driver = GraphDatabase.driver(uri, auth=("neo4j", "toss1234"))
    
    query = """
    MATCH (c:Candidate)
    WHERE c.name_kr IN ['김대용', '김용'] OR c.name_kr STARTS WITH '김' AND c.name_kr ENDS WITH '용'
    RETURN c.id, c.name_kr, c.phone, c.email, c.document_hash
    """
    
    # Just to trace if it's the specific "김용" or someone else, let's also fetch anyone with name ending in '용' if exact match finds nothing.
    actual_query = """
    MATCH (c:Candidate)
    WHERE c.name_kr IN ['김대용', '김용', '김지용', '김동용', '김태용', '김도용', '김수용', '김희용', '김진용']  
       OR c.name_kr =~ '김.*용'
    RETURN c.id, c.name_kr, c.phone, c.email, c.document_hash
    """
    
    results_found = False
    with driver.session() as session:
        result = session.run(actual_query)
        print("Neo4j Candidate Duplication Scan:")
        print("=" * 80)
        for r in result:
            results_found = True
            print(f"Name: {r['c.name_kr']:<10} | Hash/ID: {r['c.id']:<15} | Phone: {r['c.phone']:<15} | Email: {r['c.email']:<20}")
        
    driver.close()
    
    if not results_found:
        print("No candidates found matching '김*용'")

if __name__ == "__main__":
    check_dupes()
