import json, sqlite3, math
from openai import OpenAI
from neo4j import GraphDatabase

secrets = json.load(open('secrets.json', encoding='utf-8'))
client = OpenAI(api_key=secrets['OPENAI_API_KEY'])
driver = GraphDatabase.driver(secrets['NEO4J_URI'], auth=(secrets['NEO4J_USERNAME'], secrets['NEO4J_PASSWORD']))

query_text = "카카오 출신 백엔드 시니어 개발자"
emb_res = client.embeddings.create(input=[query_text], model="text-embedding-3-small")
query_vector = emb_res.data[0].embedding

target_id = 'ba99c86f-562d-4193-8380-0e414bd19093' # 배성호

def cosine_similarity(v1, v2):
    dot = sum(a*b for a, b in zip(v1, v2))
    norm1 = math.sqrt(sum(a*a for a in v1))
    norm2 = math.sqrt(sum(b*b for b in v2))
    if norm1 == 0 or norm2 == 0: return 0.0
    return dot / (norm1 * norm2)

def get_best_similarity(query_vec, main_sim, career_embs_json):
    if not career_embs_json:
        return main_sim
    try:
        career_embs = json.loads(career_embs_json)
        if not career_embs:
            return main_sim
        career_sims = [cosine_similarity(query_vec, e)
                       for e in career_embs]
        best = max(career_sims)
        return 0.80 * main_sim + 0.20 * best
    except:
        return main_sim

# Simulate BM25 retrieving 배성호 (since he has "카카오" in raw_text)
combined_ids = [target_id]

with driver.session() as session:
    res = session.run("""
        MATCH (c:Candidate) WHERE c.id IN $ids
        RETURN c.id AS id, c.embedding AS embedding, c.career_embeddings_json AS career_embeddings_json
    """, ids=combined_ids)
    
    for r in res:
        cid = r['id']
        emb = r['embedding']
        career_json = r['career_embeddings_json']
        
        main_sim = cosine_similarity(query_vector, emb)
        blended = get_best_similarity(query_vector, main_sim, career_json)
        
        print(f"Candidate: 배성호")
        print(f"  Main Sim: {main_sim:.4f}")
        print(f"  Blended Sim: {blended:.4f}")

driver.close()
