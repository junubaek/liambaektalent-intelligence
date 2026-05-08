import sqlite3, json
from neo4j import GraphDatabase
from pinecone import Pinecone

cid = '8a8f2be2-8a1a-4acc-8a59-e006f3907697'
secrets = json.load(open('secrets.json'))

# 1. Neo4j 삭제 (남은 작업)
try:
    driver = GraphDatabase.driver(secrets['NEO4J_URI'], auth=(secrets['NEO4J_USERNAME'], secrets['NEO4J_PASSWORD']))
    with driver.session() as session:
        session.run('MATCH (c:Candidate {id: $cid}) DETACH DELETE c', cid=cid)
    print(f'Neo4j node {cid} deleted successfully.')
    driver.close()
except Exception as e:
    print(f'Neo4j deletion failed: {e}')

# 2. Pinecone 삭제 (남은 작업)
try:
    pc = Pinecone(api_key=secrets['PINECONE_API_KEY'])
    index = pc.Index(secrets['PINECONE_INDEX_NAME'])
    index.delete(ids=[cid])
    print(f'Pinecone vector {cid} deleted successfully.')
except Exception as e:
    print(f'Pinecone deletion failed: {e}')
