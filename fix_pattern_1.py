import json
from neo4j import GraphDatabase

NEO4J_URI = "neo4j://127.0.0.1:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "toss1234"
PROGRESS_FILE = r"C:\Users\cazam\Downloads\이력서자동분석검색시스템\processed.json"

driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

def check_missing_candidates():
    # 1. Get from Neo4j
    neo4j_names = set()
    with driver.session() as session:
        result = session.run("MATCH (c:Candidate) RETURN c.name AS name")
        for record in result:
            neo4j_names.add(record["name"])
            
    # 2. Get from processed.json
    try:
        with open(PROGRESS_FILE, "r", encoding="utf-8") as f:
            processed = json.load(f)
            processed_names = set(processed.keys())
    except Exception as e:
        print(f"Error loading processed.json: {e}")
        return

    # Check totals
    print(f"Total in processed.json: {len(processed_names)}")
    print(f"Total Candidate nodes in Neo4j: {len(neo4j_names)}")
    
    missing_names = processed_names - neo4j_names
    print(f"Number of missing candidates: {len(missing_names)}")

    # Reason analysis check
    # Many might be empty dictionary values in processed or skipped parsing (e.g. hash dupes)
    # or Gemini returned []
    hash_dupes = 0
    empty_parsed = 0
    for name in missing_names:
        meta = processed.get(name, {})
        # If it's hash dupe, maybe it doesn't have edges? Wait, text_hash might be empty for failures
        pass

    with open("missing_candidates.txt", "w", encoding="utf-8") as f:
        for name in missing_names:
            f.write(name + "\n")
            
    print("Saved missing candidates to missing_candidates.txt")

if __name__ == "__main__":
    check_missing_candidates()
