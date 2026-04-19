import os, json
from neo4j import GraphDatabase

PROGRESS_FILE = r"C:\Users\cazam\Downloads\이력서자동분석검색시스템\processed.json"
if os.path.exists(PROGRESS_FILE):
    os.remove(PROGRESS_FILE)
    print(f"Deleted {PROGRESS_FILE}")

NEO4J_URI = "neo4j://127.0.0.1:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "toss1234"

try:
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
    with driver.session() as session:
        res = session.run("MATCH (c:Candidate)-[r]->(s:Skill) WHERE type(r) <> 'HAS_SKILL' DELETE r")
        summary = res.consume()
        print(f"Deleted {summary.counters.relationships_deleted} old dynamic relationships (edges).")
    driver.close()
    print("Reset complete!")
except Exception as e:
    print("Error:", e)
