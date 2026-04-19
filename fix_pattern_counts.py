import os
import json
from neo4j import GraphDatabase

NEO4J_URI = "neo4j://127.0.0.1:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "toss1234"
driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

FOLDER1 = r"C:\Users\cazam\Downloads\02_resume 전처리"
FOLDER2 = r"C:\Users\cazam\Downloads\02_resume_converted_docx"
PROGRESS_FILE = r"C:\Users\cazam\Downloads\이력서자동분석검색시스템\processed.json"

def analyze_all():
    files_dict = {}
    if os.path.exists(FOLDER1):
        for f in os.listdir(FOLDER1):
            name = f.rsplit(".", 1)[0]
            files_dict[name] = os.path.join(FOLDER1, f)
    if os.path.exists(FOLDER2):
        for f in os.listdir(FOLDER2):
            name = f.rsplit(".", 1)[0]
            files_dict[name] = os.path.join(FOLDER2, f)
            
    print(f"Total files in folders: {len(files_dict)}")
    
    try:
        with open(PROGRESS_FILE, "r", encoding="utf-8") as f:
            processed = json.load(f)
            processed_names = set(processed.keys())
    except Exception as e:
        processed_names = set()
        
    print(f"Total in processed.json: {len(processed_names)}")
        
    neo4j_names = set()
    with driver.session() as session:
        result = session.run("MATCH (c:Candidate) RETURN c.name AS name")
        for record in result:
            neo4j_names.add(record["name"])
            
    print(f"Total in Neo4j: {len(neo4j_names)}")
    
    missing_from_neo4j = set(files_dict.keys()) - neo4j_names
    print(f"Total missing from Neo4j out of physical files: {len(missing_from_neo4j)}")
    
    with open("missing_candidates.txt", "w", encoding="utf-8") as f:
        for name in missing_from_neo4j:
            f.write(name + "\n")

if __name__ == "__main__":
    analyze_all()
