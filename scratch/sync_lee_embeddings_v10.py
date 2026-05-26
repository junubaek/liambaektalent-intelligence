import json, sqlite3, sys, os
sys.stdout.reconfigure(encoding='utf-8')
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT_DIR)

from openai import OpenAI
from neo4j import GraphDatabase
from run_neo4j_embedding_expansion import build_emb_text

def update_lee_sang_heon_embeddings_reinforced():
    os.chdir(ROOT_DIR)
    with open('secrets.json', 'r', encoding='utf-8') as f:
        secrets = json.load(f)
    oai = OpenAI(api_key=secrets['OPENAI_API_KEY'])
    driver = GraphDatabase.driver(
        secrets['NEO4J_URI'],
        auth=(secrets['NEO4J_USERNAME'], secrets['NEO4J_PASSWORD'])
    )

    conn = sqlite3.connect('candidates.db')
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    targets = {
        '898ea4e0-77d4-46d5-bf4d-c2d5b4a04741': 'Global_Sales_and_Marketing B2B_Sales Overseas_Sales',
        'db752f0f-0f1a-437c-a09d-43c20442ab7b': 'General_Affairs Procurement_Buyer Administrative_Management',
        '55726c4a-4601-4ee9-87dc-581d15eda75e': 'Bioinformatics Machine_Learning Data_Science Bioinformatics_Pipeline_Automation'
    }

    for cid, reinforcement in targets.items():
        print(f"Updating REINFORCED embedding for {cid}...")
        cur.execute("SELECT id, name_kr, sector, profile_summary, raw_text FROM candidates WHERE id = ?", (cid,))
        row = cur.fetchone()
        if not row:
            continue
        
        base_emb_text = build_emb_text(row)
        reinforced_text = f"{reinforcement}\n{reinforcement}\n{base_emb_text}"
        
        sample = reinforced_text[:120].replace('\n', ' ')
        print(f"  Reinforced Text (Sample): {sample}...")
        
        resp = oai.embeddings.create(model='text-embedding-3-small', input=[reinforced_text])
        embedding = resp.data[0].embedding
        
        with driver.session() as s:
            s.run("MATCH (c:Candidate {id: $id}) SET c.embedding = $emb", id=cid, emb=embedding)
        print(f"  ✅ Updated.")

    conn.close()
    driver.close()

if __name__ == '__main__':
    update_lee_sang_heon_embeddings_reinforced()
