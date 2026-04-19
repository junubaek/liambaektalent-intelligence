import sys
import os

ROOT_DIR = r"c:\Users\cazam\Downloads\이력서자동분석검색시스템"
sys.path.append(ROOT_DIR)

from neo4j import GraphDatabase

driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "toss1234"))

with driver.session() as session:
    res = session.run("MATCH (s:Skill) WHERE NOT (s)--() DELETE s RETURN COUNT(s) as deleted")
    # Actually DELETE doesn't return count directly easily if deleted, so just do separate query
    
with driver.session() as session:
    res = session.run("MATCH (s:Skill) WHERE NOT (s)--() RETURN count(s) as c")
    print(f"Remaining ghost nodes: {res.single()['c']}")

driver.close()
