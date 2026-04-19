import json
from neo4j import GraphDatabase

def main():
    driver = GraphDatabase.driver('neo4j://127.0.0.1:7687', auth=('neo4j', 'toss1234'))
    
    # Fast query to get all candidate names that actually have edges
    with driver.session() as session:
        results = session.run("MATCH (c:Candidate)-[r]->() RETURN DISTINCT c.name AS name")
        valid_names = set(record["name"] for record in results)
        
    print(f"Total candidates with edges in Neo4j: {len(valid_names)}")
    
    with open('processed.json', 'r', encoding='utf-8') as f:
        processed = json.load(f)
        
    missing = [name for name in processed if name not in valid_names]
    print(f"Found {len(missing)} candidates marked processed but missing edges.")
    
    for name in missing:
        processed.pop(name, None)
        
    with open('processed.json', 'w', encoding='utf-8') as f:
        json.dump(processed, f, ensure_ascii=False, indent=2)
        
    print("Fixed processed.json.")

if __name__ == "__main__":
    main()
