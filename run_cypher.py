import json
from neo4j import GraphDatabase

def run():
    uri = "neo4j://127.0.0.1:7687"
    driver = GraphDatabase.driver(uri, auth=("neo4j", "toss1234"))
    
    query = """
    MATCH (c:Candidate)
    WHERE c.name_kr IN ['김대용', '김용']
    RETURN c.id, c.document_hash, c.phone, c.email
    """
    
    with driver.session() as session:
        result = session.run(query)
        print(f"{'id':<18} | {'document_hash':<35} | {'phone':<15} | {'email':<20}")
        print("-" * 100)
        count = 0
        for r in result:
            id_str = str(r['c.id'])
            hash_str = str(r['c.document_hash'])
            phone_str = str(r['c.phone'])
            email_str = str(r['c.email'])
            print(f"{id_str:<18} | {hash_str:<35} | {phone_str:<15} | {email_str:<20}")
            count += 1
        print(f"\nTotal match: {count}")
    driver.close()

if __name__ == "__main__":
    run()
