import json
from neo4j import GraphDatabase

with open('secrets.json', 'r', encoding='utf-8') as f:
    secrets = json.load(f)
    
driver = GraphDatabase.driver(
    secrets['NEO4J_URI'],
    auth=(secrets['NEO4J_USERNAME'], secrets['NEO4J_PASSWORD'])
)

with driver.session() as session:
    # Check how many Experience_Chunk nodes exist in Neo4j Aura
    cnt = session.run("MATCH (e:Experience_Chunk) RETURN count(e)").single()[0]
    print(f"Total Experience_Chunk nodes in Neo4j Aura: {cnt}개")
    
    # Check how many of them are NOT connected to any Candidate node
    orphaned_cnt = session.run("MATCH (e:Experience_Chunk) WHERE NOT (:Candidate)-[:HAS_EXPERIENCE]->(e) RETURN count(e)").single()[0]
    print(f"Orphaned Experience_Chunk nodes (not connected to Candidate): {orphaned_cnt}개")
    
driver.close()
