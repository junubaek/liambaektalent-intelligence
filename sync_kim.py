import os, sqlite3, json
from openai import OpenAI
from neo4j import GraphDatabase

def sync_target():
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
    
    # 2. Extract Skills
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        with open("secrets.json", "r", encoding='utf-8') as f:
            api_key = json.load(f).get("OPENAI_API_KEY")
    
    client = OpenAI(api_key=api_key)
    res = client.chat.completions.create(
        model="gpt-4o-mini",
        response_format={ "type": "json_object" },
        messages=[
            {"role": "system", "content": "Extract skills and actions (BUILT, IMPROVED, LED, ANALYZED, MAINTAINED, USED) from resume in JSON: {\"skills\": [{\"skill\": \"...\", \"action\": \"...\"}]}"},
            {"role": "user", "content": raw_text[:6000]}
        ]
    )
    skills = json.loads(res.choices[0].message.content).get("skills", [])
    print(f"Extracted {len(skills)} skills for {name}")

    # 3. Sync to Neo4j
    uri = os.environ.get("NEO4J_URI", "bolt://localhost:7687")
    user = os.environ.get("NEO4J_USERNAME", "neo4j")
    pwd = os.environ.get("NEO4J_PASSWORD", "toss1234")
    
    driver = GraphDatabase.driver(uri, auth=(user, pwd))
    with driver.session() as session:
        session.run("""
            MERGE (c:Candidate {id: $id})
            SET c.name_kr = $name, c.name = $name, c.email = $email, c.phone = $phone
        """, id=target_id, name=name, email=email or "", phone=phone or "")
        
        for s in skills:
            session.run("""
                MATCH (c:Candidate {id: $id})
                MERGE (sk:Skill {name: $sname})
                MERGE (c)-[r:HAS_SKILL]->(sk)
                SET r.action = $action
            """, id=target_id, sname=s['skill'], action=s['action'])
    driver.close()
    print(f"Successfully synced {name} to Neo4j")

if __name__ == "__main__":
    sync_target()
