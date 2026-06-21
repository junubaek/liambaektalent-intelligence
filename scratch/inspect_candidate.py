from neo4j import GraphDatabase
import json

secrets = json.load(open('secrets.json', encoding='utf-8'))
driver = GraphDatabase.driver(secrets['NEO4J_URI'], auth=(secrets['NEO4J_USERNAME'], secrets['NEO4J_PASSWORD']))

ids = [
    'ba99c86f-562d-4193-8380-0e414bd19093', # 배성호 (Kakao)
    'ae1ac997-651e-4c0d-9809-7d5d0b2f521b', # 이민식 (Samsung)
    'ca4146b1-7c15-4854-8d90-80036bf284a9', # 임채운 (Toss)
    'cf822061-7f61-4aad-bdde-345ed0d334c0', # 이용복 (Naver)
    '18b0c77b-9d05-4f44-b210-4f08f0af74ef'  # 임학주 (Rebellions)
]

with driver.session() as session:
    for cid in ids:
        res = session.run("""
            MATCH (c:Candidate {id: $id})
            RETURN c.name_kr as name, c.career_embeddings_json as embs, keys(c) as keys
        """, id=cid)
        row = res.single()
        if row:
            print(f"Name: {row['name']} ({cid})")
            print(f"  Keys: {row['keys']}")
            embs = row['embs']
            print(f"  Has career_embeddings_json: {embs is not None}")
            if embs:
                try:
                    loaded = json.loads(embs)
                    print(f"  Embeddings count: {len(loaded)}")
                except Exception as e:
                    print(f"  Parse error: {e}")
        else:
            print(f"Candidate ID {cid} not found in Neo4j.")

driver.close()
