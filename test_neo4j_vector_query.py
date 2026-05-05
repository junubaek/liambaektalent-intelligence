from neo4j import GraphDatabase
from openai import OpenAI
import json

with open("secrets.json", "r") as f:
    secrets = json.load(f)
client = OpenAI(api_key=secrets.get("OPENAI_API_KEY"))

driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "toss1234"))

query = "senior cfo"
emb_res = client.embeddings.create(input=[query], model="text-embedding-3-small")
query_vector = emb_res.data[0].embedding

target_id = "f5875fc2-99aa-4605-9742-5ec93f4cd51a"

with driver.session() as session:
    print(f"--- Querying Neo4j Vector Index for '{query}' ---")
    res = session.run("""
        CALL db.index.vector.queryNodes('candidate_embedding', 300, $queryVector)
        YIELD node AS c, score
        RETURN c.id AS id, c.name_kr AS name, score
    """, queryVector=query_vector)
    
    found = False
    results = list(res)
    for i, r in enumerate(results):
        if r['id'] == target_id:
            print(f"FOUND {r['name']} ({r['id']}) at Rank {i+1} with Vector Score: {r['score']}")
            found = True
            break
    
    if not found:
        print(f"Kim Eun-hyung not found in top {len(results)} vector results.")
        # Check her raw embedding
        res_raw = session.run("MATCH (n:Candidate {id: $id}) RETURN n.name_kr, n.embedding IS NOT NULL as has_emb", id=target_id)
        for r in res_raw:
            print(f"Raw check: {r['n.name_kr']} has_emb={r['has_emb']}")

driver.close()
