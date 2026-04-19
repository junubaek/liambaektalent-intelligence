import time
from neo4j import GraphDatabase
d = GraphDatabase.driver('bolt://localhost:7687', auth=('neo4j','toss1234'))
from connectors.openai_api import OpenAIClient
import json
secrets = json.load(open('secrets.json','r'))
openai = OpenAIClient(secrets['OPENAI_API_KEY'])
vec = openai.embed_content('vLLM 최적화 배포 NPU 인프라 구축 NPU/CUDA NPU')

with d.session() as s: 
    s.run('''
        MERGE (c:Candidate {name_kr: '오원교[Test]'})
        SET c.id = 'test_hash_001', c.company = 'Toss', c.phone = '010-0000-0000'
        MERGE (e:Experience_Chunk {id: 'test_chunk_001'})
        SET e.company_name = 'Toss', e.end_date = '현재', e.description = 'vLLM 배포', e.embedding = $vec
        MERGE (c)-[x:HAS_EXPERIENCE]->(e)
        MERGE (sk:Skill {name: 'vLLM'})
        MERGE (e)-[r:BUILT]->(sk)
    ''', vec=vec)
d.close()
print('Dummy Inserted')
