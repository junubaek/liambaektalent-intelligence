from neo4j import GraphDatabase
import json, os, sys
sys.stdout.reconfigure(encoding='utf-8')
# Load secrets
secrets_path = os.path.join(os.path.dirname(__file__), '..', 'secrets.json')
with open(secrets_path, encoding='utf-8') as f:
    s = json.load(f)
driver = GraphDatabase.driver(s['NEO4J_URI'], auth=(s['NEO4J_USERNAME'], s['NEO4J_PASSWORD']))
skills = [
    ('32022567-1b6f-81ef-a8f5-e3a0cd6dd030','Ethernet_Verification','BUILT'),
    ('32022567-1b6f-81ef-a8f5-e3a0cd6dd030','Automotive_Ethernet','BUILT'),
    ('69c34de3-000e-443e-b438-4f1cafb5e1db','Public_Relations','MANAGED'),
    ('69c34de3-000e-443e-b438-4f1cafb5e1db','Tech_PR','MANAGED'),
    ('c3d4ee55-266a-44f6-8e66-fb7486be38a8','Partner_Alliance','MANAGED'),
    ('c3d4ee55-266a-44f6-8e66-fb7486be38a8','Enterprise_Sales','MANAGED'),
    ('31f22567-1b6f-816c-ac76-f6ac6c31c2db','Power_Grid_Engineering','BUILT'),
    ('31f22567-1b6f-816c-ac76-f6ac6c31c2db','Smart_Grid','BUILT'),
    ('1e73a38a-9c39-414e-b95d-3e522183ed27','Chief_Operating_Officer','MANAGED'),
    ('07043d62-db55-458e-a43e-2243d30f4065','Kafka_Infrastructure','BUILT'),
    ('8454b89a-4474-4787-8c07-3b8a9e937a45','Technical_Leadership','MANAGED'),
]
with driver.session() as session:
    for cid, skill, rel in skills:
        session.run(
            f"MATCH (c:Candidate {{id:$cid}}) MERGE (s:Skill {{name:$skill}}) MERGE (c)-[:{rel}]->(s)",
            cid=cid,
            skill=skill
        )
driver.close()
print('Neo4j 스킬 추가 완료')
