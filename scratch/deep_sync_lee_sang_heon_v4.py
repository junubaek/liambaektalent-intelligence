import os, sqlite3, json, sys, time, re
sys.stdout.reconfigure(encoding='utf-8')

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT_DIR)

from connectors.gemini_api import GeminiClient
from connectors.openai_api import OpenAIClient
from neo4j import GraphDatabase
from ontology_graph import CANONICAL_MAP

with open('secrets.json', 'r', encoding='utf-8') as f:
    secrets = json.load(f)

gemini = GeminiClient(secrets["GEMINI_API_KEY"])
openai = OpenAIClient(secrets["OPENAI_API_KEY"])
driver = GraphDatabase.driver(secrets["NEO4J_URI"], auth=(secrets["NEO4J_USERNAME"], secrets["NEO4J_PASSWORD"]))

def normalize_skill(sname):
    # Try direct match
    if sname in CANONICAL_MAP:
        return CANONICAL_MAP[sname]
    
    # Try case-insensitive and whitespace-flexible match
    s_clean = re.sub(r'[^a-zA-Z0-9가-힣]', '', sname).lower()
    for k, v in CANONICAL_MAP.items():
        k_clean = re.sub(r'[^a-zA-Z0-9가-힣]', '', k).lower()
        if s_clean == k_clean:
            return v
    
    # Try if it's already a value in CANONICAL_MAP
    canonical_values = set(CANONICAL_MAP.values())
    if sname in canonical_values:
        return sname
    
    return sname # Fallback to original

def parse_and_sync(candidate_id):
    conn = sqlite3.connect('candidates.db')
    cur = conn.cursor()
    cur.execute("SELECT name_kr, raw_text, current_company FROM candidates WHERE id = ?", (candidate_id,))
    row = cur.fetchone()
    if not row:
        print(f"Candidate {candidate_id} not found in SQLite.")
        return
    
    name, text, company = row
    print(f"--- Processing {name} ({candidate_id[:8]}) ---")
    
    # 1. Embedding
    print(f"  Calculating embedding...")
    embedding = openai.embed_content(text[:8000])
    
    # 2. Parsing
    print(f"  Parsing with Gemini...")
    prompt = f"""
Analyze the following resume and extract professional skills and a summary.
Candidate: {name}
Company: {company}

[RESUME TEXT]
{text}

[OUTPUT FORMAT]
JSON only:
{{
  "summary": "Professional summary",
  "skills": ["Skill1", "Skill2", ...],
  "seniority": "Junior|Middle|Senior",
  "sector": "Main Sector Name"
}}
"""
    try:
        res = gemini.get_chat_completion_json(prompt, model="gemini-3-flash-preview")
        if not res: return
        
        summary = res.get("summary", "")
        raw_skills = res.get("skills", [])
        sector = res.get("sector", "Unknown")
        seniority = res.get("seniority", "Middle")
        
        # Normalize skills
        skills = list(set([normalize_skill(s) for s in raw_skills]))
        print(f"  Normalized skills: {skills}")
        
        # Update SQLite
        cur.execute("""
            UPDATE candidates 
            SET profile_summary = ?, sector = ?, is_neo4j_synced = 1
            WHERE id = ?
        """, (summary, sector, candidate_id))
        conn.commit()
        
        # Update Neo4j
        with driver.session() as session:
            session.run("""
                MERGE (c:Candidate {id: $id})
                SET c.name = $name, c.company = $company, c.profile_summary = $summary, 
                    c.sector = $sector, c.seniority = $seniority, c.embedding = $embedding
            """, id=candidate_id, name=name, company=company, summary=summary, sector=sector, seniority=seniority, embedding=embedding)
            
            session.run("MATCH (c:Candidate {id: $id})-[r:HAS_SKILL]->() DELETE r", id=candidate_id)
            for sname in skills:
                session.run("""
                    MATCH (c:Candidate {id: $id})
                    MERGE (s:Skill {name: $sname})
                    MERGE (c)-[:HAS_SKILL]->(s)
                """, id=candidate_id, sname=sname)
        
        print(f"  Successfully parsed and synced {len(skills)} skills and embedding.")
        
    except Exception as e:
        print(f"  Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    target_ids = [
        '898ea4e0-77d4-46d5-bf4d-c2d5b4a04741', # Sales
        'db752f0f-0f1a-437c-a09d-43c20442ab7b', # GA
        '55726c4a-4601-4ee9-87dc-581d15eda75e'  # Bio
    ]
    for tid in target_ids:
        parse_and_sync(tid)
    driver.close()
