import os, sqlite3, json
from openai import OpenAI
from neo4j import GraphDatabase

def sync_target_aura():
    target_id = 'f5875fc2-99aa-4605-9742-5ec93f4cd51a'
    
    # 1. Get from SQLite
    conn = sqlite3.connect('candidates.db')
    cur = conn.cursor()
    cur.execute("SELECT name_kr, email, phone, raw_text FROM candidates WHERE id=?", (target_id,))
    row = cur.fetchone()
    conn.close()
    
    if not row:
        print("Candidate not found in SQLite")
        return
    
    name, email, phone, raw_text = row
    
    # 2. Get Secrets
    with open("secrets.json", "r", encoding='utf-8') as f:
        secrets = json.load(f)
    
    api_key = secrets.get("OPENAI_API_KEY")
    client = OpenAI(api_key=api_key)
    
    print(f"Generating embedding for {name}...")
    emb_res = client.embeddings.create(input=[raw_text[:8000]], model="text-embedding-3-small")
    embedding = emb_res.data[0].embedding
    
    # 3. Sync to Neo4j Aura
    uri = secrets.get("NEO4J_URI")
    user = secrets.get("NEO4J_USERNAME")
    pwd = secrets.get("NEO4J_PASSWORD")
    
    print(f"Syncing {name} to Neo4j Aura: {uri}...")
    driver = GraphDatabase.driver(uri, auth=(user, pwd))
    with driver.session() as session:
        # Create/Update node
        session.run("""
            MERGE (c:Candidate {id: $id})
            SET c.name_kr = $name, c.name = $name, c.email = $email, c.phone = $phone, c.embedding = $embedding
        """, id=target_id, name=name, email=email or "", phone=phone or "", embedding=embedding)
        
        # Add Chief_Financial_Officer skill
        session.run("""
            MATCH (c:Candidate {id: $id})
            MERGE (sk:Skill {name: 'Chief_Financial_Officer'})
            MERGE (c)-[r:HAS_SKILL]->(sk)
            SET r.action = 'MANAGED'
        """, id=target_id)
        
        # Extract and add other skills for completeness
        print("Extracting additional skills...")
        res_llm = client.chat.completions.create(
            model="gpt-4o-mini",
            response_format={ "type": "json_object" },
            messages=[
                {"role": "system", "content": "Extract skills and actions from resume in JSON: {\"skills\": [{\"skill\": \"...\", \"action\": \"...\"}]}"},
                {"role": "user", "content": raw_text[:6000]}
            ]
        )
        skills = json.loads(res_llm.choices[0].message.content).get("skills", [])
        for s in skills:
            session.run("""
                MATCH (c:Candidate {id: $id})
                MERGE (sk:Skill {name: $sname})
                MERGE (c)-[r:HAS_SKILL]->(sk)
                SET r.action = $action
            """, id=target_id, sname=s['skill'], action=s['action'])
            
    driver.close()
    print(f"Successfully synced {name} to Neo4j Aura")

if __name__ == "__main__":
    sync_target_aura()
