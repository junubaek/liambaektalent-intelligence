import sqlite3, json, sys
sys.stdout.reconfigure(encoding='utf-8')
from neo4j import GraphDatabase

secrets = json.load(open('secrets.json'))
driver = GraphDatabase.driver(secrets['NEO4J_URI'], auth=(secrets['NEO4J_USERNAME'], secrets['NEO4J_PASSWORD']))

bio_ids = ['ba6d2583-fac1-474b-9df7-ee1b265ae34f', '55726c4a-4601-4ee9-87dc-581d15eda75e']

with driver.session() as session:
    for bid in bio_ids:
        print(f"--- Bio ID {bid} 조회 ---")
        node = session.run('MATCH (c:Candidate {id: $cid}) RETURN c.name, c.company', cid=bid).single()
        if node:
            print(f"Neo4j 존재: {node['c.name']}, {node['c.company']}")
            skills = session.run('MATCH (c:Candidate {id: $cid})-->(s:Skill) RETURN s.name', cid=bid).data()
            print(f"스킬: {len(skills)}개")
        else:
            print("Neo4j에 존재하지 않음")
        print("-" * 30)

driver.close()
