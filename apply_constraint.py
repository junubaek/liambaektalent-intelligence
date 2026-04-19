import io, sys
sys.stdout=io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from neo4j import GraphDatabase
driver=GraphDatabase.driver('neo4j://127.0.0.1:7687', auth=('neo4j','toss1234'))
with driver.session() as session:
    try:
        session.run('CREATE CONSTRAINT skill_name_unique IF NOT EXISTS FOR (s:Skill) REQUIRE s.name IS UNIQUE')
        print('✅ CONSTRAINT APPLIED SUCCESSFULLY')
    except Exception as e:
        print(f"Error: {e}")
 driver.close()
