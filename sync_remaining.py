import sqlite3
import json
from neo4j import GraphDatabase
from ontology_graph import CANONICAL_MAP

# Load secrets
with open("secrets.json", "r", encoding="utf-8") as f:
    secrets = json.load(f)

n_uri = secrets.get("NEO4J_URI", "neo4j://127.0.0.1:7687")
n_user = secrets.get("NEO4J_USERNAME", "neo4j")
n_pw = secrets.get("NEO4J_PASSWORD", "toss1234")

# Extract top skills locally
def extract_top_idf_skills(text: str, n: int = 7) -> list:
    if not text:
        return []
    try:
        with open('node_idf.json', 'r', encoding='utf-8') as f:
            idf_map = json.load(f)
    except:
        idf_map = {}
        
    text_lower = text.lower()
    matched_skills = {}
    
    for alias, canonical in CANONICAL_MAP.items():
        if len(alias) > 1 and alias.lower() in text_lower:
            idf_val = idf_map.get(canonical, 1.5)
            if canonical not in matched_skills or idf_val > matched_skills[canonical]:
                matched_skills[canonical] = idf_val
                
    for skill_name, idf_val in idf_map.items():
        skill_clean = skill_name.replace('_', ' ').lower()
        if len(skill_clean) > 2 and (skill_clean in text_lower or skill_name.lower() in text_lower):
            if skill_name not in matched_skills or idf_val > matched_skills[skill_name]:
                matched_skills[skill_name] = idf_val
                
    sorted_skills = sorted(matched_skills.items(), key=lambda x: x[1], reverse=True)
    return [s[0] for s in sorted_skills[:n]]

# Find missing candidate IDs
driver = GraphDatabase.driver(n_uri, auth=(n_user, n_pw))
with driver.session() as session:
    result = session.run('MATCH (c:Candidate) RETURN c.id as id')
    neo4j_ids = {r['id'] for r in result}

conn = sqlite3.connect('candidates.db')
cur = conn.cursor()
cur.execute('SELECT id, name_kr, phone, email, current_company, profile_summary, total_years, sector, raw_text FROM candidates WHERE is_duplicate=0')
candidates = cur.fetchall()

missing_candidates = [c for c in candidates if c[0] not in neo4j_ids]
print(f"Remaining Neo4j 누락: {len(missing_candidates)}명")

# Sync remaining
ok = 0
fail = 0

with driver.session() as session:
    for c in missing_candidates:
        cid, name, phone, email, company, summary, total_years, sector, raw_text = c
        try:
            print(f"Syncing {name} ({cid})...")
            # Create Candidate node
            res = session.run("""
                MERGE (c:Candidate {id: $id})
                SET c.name = $name, c.phone = $phone, c.email = $email,
                    c.current_company = $company, c.profile_summary = $summary,
                    c.total_years = $total_years, c.sector = $sector
                RETURN c
            """, id=cid, name=name, phone=phone, email=email, company=company, summary=summary, total_years=total_years, sector=sector)
            
            # Check result
            summary_res = res.consume()
            print(f"  Candidate MERGE: counters={summary_res.counters}")
            
            # Local Skill extraction and Edge generation
            skills = extract_top_idf_skills(raw_text, n=7)
            for skill in skills:
                res_edge = session.run("""
                    MERGE (c:Candidate {id: $id})
                    MERGE (s:Skill {name: $skill})
                    MERGE (c)-[r:BUILT]->(s)
                    SET r.confidence = 0.8, r.evidence_span = 'Local ID-IDF extraction sync', r.source = 'missing_sync'
                    RETURN r
                """, id=cid, skill=skill)
                res_edge.consume()
            
            ok += 1
        except Exception as e:
            fail += 1
            print(f"  Error: {e}")

conn.close()
driver.close()

print(f"완료: 성공={ok}, 실패={fail}")
