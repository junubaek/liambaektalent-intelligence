import json
from neo4j import GraphDatabase

secrets = json.load(open('secrets.json'))
driver = GraphDatabase.driver(secrets['NEO4J_URI'], auth=(secrets['NEO4J_USERNAME'], secrets['NEO4J_PASSWORD']))
with driver.session() as session:
    # DevOps 엣지 확인
    res = session.run('MATCH (c:Candidate {name_kr: "강기태"})-[r]->(s:Skill {name: "DevOps"}) RETURN type(r) as rel_type, properties(r) as props').single()
    if res:
        print(f"DevOps Edge: {res['rel_type']} | Props: {res['props']}")
    
    # SCM 엣지 확인 (무관한 것)
    res2 = session.run('MATCH (c:Candidate {name_kr: "강기태"})-[r]->(s:Skill {name: "SCM"}) RETURN type(r) as rel_type, properties(r) as props').single()
    if res2:
        print(f"SCM Edge: {res2['rel_type']} | Props: {res2['props']}")
driver.close()
