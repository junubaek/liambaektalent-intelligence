import json
from neo4j import GraphDatabase
secrets = json.load(open('secrets.json'))
driver = GraphDatabase.driver(secrets['NEO4J_URI'], auth=(secrets['NEO4J_USERNAME'], secrets['NEO4J_PASSWORD']))
session = driver.session()

cid = 'c3d4ee55-266a-44f6-8e66-fb7486be38a8'
res = session.run('''
    MATCH (c:Candidate {id: $cid})
    RETURN c.id as id, c.name_kr as name,
           c.embedding IS NOT NULL as has_embedding,
           size(c.embedding) as emb_size
''', cid=cid).data()
print(f'Choi Woo-sung: {res}')

# Total stats
stats = session.run('''
    MATCH (c:Candidate)
    RETURN 
        count(c) as total,
        sum(CASE WHEN c.embedding IS NOT NULL THEN 1 ELSE 0 END) as with_emb,
        sum(CASE WHEN c.embedding IS NULL THEN 1 ELSE 0 END) as without_emb
''').single()
print(f'Total Candidates: {stats["total"]}')
print(f'With Embedding: {stats["with_emb"]}')
print(f'Without Embedding: {stats["without_emb"]}')
driver.close()
