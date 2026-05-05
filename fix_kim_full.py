import os, sqlite3, json
from openai import OpenAI
from neo4j import GraphDatabase

def fix_kim():
    target_id = 'f5875fc2-99aa-4605-9742-5ec93f4cd51a'
    
    # 1. Get from SQLite
    conn = sqlite3.connect('candidates.db')
    cur = conn.cursor()
    cur.execute("SELECT name_kr, raw_text FROM candidates WHERE id=?", (target_id,))
    row = cur.fetchone()
    conn.close()
    
    if not row:
        print("Candidate not found")
        return
    
    name, raw_text = row
    
    # 2. Get Embedding
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        with open("secrets.json", "r", encoding='utf-8') as f:
            api_key = json.load(f).get("OPENAI_API_KEY")
    
    client = OpenAI(api_key=api_key)
    print(f"Generating embedding for {name}...")
    emb_res = client.embeddings.create(input=[raw_text[:8000]], model="text-embedding-3-small")
    embedding = emb_res.data[0].embedding
    
    # 3. Update Neo4j
    uri = os.environ.get("NEO4J_URI", "bolt://localhost:7687")
    user = os.environ.get("NEO4J_USERNAME", "neo4j")
    pwd = os.environ.get("NEO4J_PASSWORD", "toss1234")
    
    driver = GraphDatabase.driver(uri, auth=(user, pwd))
    with driver.session() as session:
        # Update node with embedding
        session.run("""
            MATCH (c:Candidate {id: $id})
            SET c.embedding = $embedding
        """, id=target_id, embedding=embedding)
        
        # Add Chief_Financial_Officer skill explicitly
        session.run("""
            MATCH (c:Candidate {id: $id})
            MERGE (sk:Skill {name: 'Chief_Financial_Officer'})
            MERGE (c)-[r:HAS_SKILL]->(sk)
            SET r.action = 'MANAGED'
        """, id=target_id)
        
    driver.close()
    print(f"Successfully fixed {name} with embedding and CFO skill")

if __name__ == "__main__":
    fix_kim()
