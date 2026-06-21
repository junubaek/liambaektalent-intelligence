import sqlite3
import json
import sys
from neo4j import GraphDatabase
from openai import OpenAI

sys.stdout.reconfigure(encoding='utf-8')

with open('secrets.json', encoding='utf-8') as f:
    secrets = json.load(f)

openai_client = OpenAI(api_key=secrets['OPENAI_API_KEY'])
driver = GraphDatabase.driver(
    secrets['NEO4J_URI'],
    auth=(secrets['NEO4J_USERNAME'], secrets['NEO4J_PASSWORD'])
)

conn = sqlite3.connect('candidates.db')
cur = conn.cursor()

targets = [
    ('한경환', '1aaad2d3-348d-48f7-8501-38d7c1f7df03'),
    ('김태경', 'fbc27466-7587-45e6-b459-c2920b5d71fe'),
    ('김일곤', 'e88ea471-e1eb-4c40-b5e1-7648e340fac4'),
    ('유정한', '31f22567-1b6f-8152-93ca-ca5ab3080016'),
    ('김형수', '4b4c3372-401b-4897-a9b3-d36a3ba3de37'),
    ('오수영', '32e22567-1b6f-8181-9992-d986271e941f'),
    ('배정현', 'fafa2636-cf0b-42c1-8c18-598d089e9c61'),
    ('하현재', 'ba4abc09-302e-4fd4-ae93-b8af52aed567'),
    ('김진영', '32022567-1b6f-819f-b62e-fa5ecb02e3de'),
    ('김진호', '1c3e3279-b0c5-4661-9dcf-7fa929dd47bb'),
    ('박천혁', '3d322d13-0699-4453-b70e-5a4c2aac38f9'),
]

# We borrow build_embedding_text and extract_top_idf_skills logic from ingest
from ontology_graph import CANONICAL_MAP
def extract_top_idf_skills(text: str, n: int = 7) -> list:
    text_lower = text.lower()
    matched_skills = {}
    for alias, canonical in CANONICAL_MAP.items():
        if len(alias) > 1 and alias.lower() in text_lower:
            matched_skills[canonical] = 1.5
    sorted_skills = sorted(matched_skills.items(), key=lambda x: x[1], reverse=True)
    return [s[0] for s in sorted_skills[:n]]

def build_embedding_text(candidate: dict) -> str:
    name = candidate.get('name_kr') or candidate.get('name', '')
    sector = candidate.get('sector', '')
    company = candidate.get('current_company', '')
    summary = candidate.get('profile_summary', '')
    raw = candidate.get('raw_text', '') or ''
    
    career_start = 0
    for trigger in ['경력', 'Experience', 'Work', '주요업무', '이력']:
        idx = raw.find(trigger)
        if idx != -1 and idx < len(raw) * 0.4:
            career_start = idx
            break
    career_text = raw[career_start:career_start+1500]
    top_skills = extract_top_idf_skills(raw, n=7)
    skills_str = ' '.join(top_skills)
    parts = [name, sector, company, skills_str, summary, career_text]
    return ' '.join(p for p in parts if p)

with driver.session() as session:
    for name, cid in targets:
        cur.execute('SELECT name_kr, sector, current_company, profile_summary, raw_text FROM candidates WHERE id=?', (cid,))
        row = cur.fetchone()
        if not row:
            print(f"[{name}] Candidate not found in SQLite.")
            continue
            
        cand_dict = {
            "name_kr": row[0],
            "sector": row[1],
            "current_company": row[2],
            "profile_summary": row[3],
            "raw_text": row[4]
        }
        
        emb_text = build_embedding_text(cand_dict)
        
        # Generate OpenAI embedding vector
        response = openai_client.embeddings.create(model="text-embedding-3-small", input=[emb_text])
        vector = response.data[0].embedding
        
        # Save embedding to Neo4j Aura Candidate node
        session.run("""
            MATCH (c:Candidate {id: $id})
            SET c.embedding = $emb
        """, id=cid, emb=vector)
        print(f"[{name}] Embedding generated and synced to Neo4j Aura (dimensions: {len(vector)}).")

conn.close()
driver.close()
print("Aura embedding synchronization complete.")
