import sys
from neo4j import GraphDatabase

sys.stdout.reconfigure(encoding='utf-8')
dr = GraphDatabase.driver('bolt://127.0.0.1:7687', auth=('neo4j','toss1234'))

with dr.session() as s:
    res = s.run("MATCH (c:Candidate {name_kr:'윤현진'})-[r]->(sk:Skill) RETURN sk.name as skill")
    print([r['skill'] for r in res])
    res = s.run("MATCH (c:Candidate {name_kr:'곽철현'})-[r]->(sk:Skill) RETURN sk.name as skill")
    print([r['skill'] for r in res])
