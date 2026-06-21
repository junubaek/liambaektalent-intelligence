import json, sqlite3
from openai import OpenAI
from neo4j import GraphDatabase

secrets = json.load(open('secrets.json', encoding='utf-8'))
client = OpenAI(api_key=secrets['OPENAI_API_KEY'])
driver = GraphDatabase.driver(secrets['NEO4J_URI'], auth=(secrets['NEO4J_USERNAME'], secrets['NEO4J_PASSWORD']))

query_text = "카카오 출신 백엔드 시니어 개발자"
emb_res = client.embeddings.create(input=[query_text], model="text-embedding-3-small")
query_vector = emb_res.data[0].embedding

target_id = 'ba99c86f-562d-4193-8380-0e414bd19093' # 배성호

with driver.session() as session:
    res = session.run("""
        CALL db.index.vector.queryNodes('candidate_embedding', 1000, $queryVector)
        YIELD node AS c, score
        RETURN c.id AS id, coalesce(c.name_kr, c.name) AS name, score
    """, queryVector=query_vector)
    
    found = False
    rank = 1
    for r in res:
        if r['id'] == target_id:
            print(f"Found 배성호 in vector search! Rank: {rank}, Score: {r['score']}")
            found = True
            break
        rank += 1
        
    if not found:
        print("배성호 not found in top 1000 of vector search.")

driver.close()
