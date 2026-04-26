import json, sqlite3, sys, time
sys.stdout.reconfigure(encoding='utf-8')
import google.generativeai as genai
from neo4j import GraphDatabase
from incremental_ingest_v10 import MEGA_PROMPT, calculate_career_stats

with open("secrets.json", "r", encoding="utf-8") as f:
    secrets = json.load(f)

genai.configure(api_key=secrets["GEMINI_API_KEY"])
model = genai.GenerativeModel("gemini-2.5-flash")

n_uri = secrets.get("NEO4J_URI", "neo4j://127.0.0.1:7687")
n_user = secrets.get("NEO4J_USERNAME", "neo4j")
n_pw = secrets.get("NEO4J_PASSWORD", "toss1234")
driver = GraphDatabase.driver(n_uri, auth=(n_user, n_pw))

conn = sqlite3.connect('candidates.db')
conn.row_factory = sqlite3.Row
cur = conn.cursor()

d = json.load(open('golden_dataset_v3.json', encoding='utf-8'))
all_ids = set()
for item in d:
    for rid in (item.get('relevant_ids') or []):
        all_ids.add(rid)

cur.execute('''
    SELECT id, name_kr, total_years, sector, raw_text,
           profile_summary, google_drive_url
    FROM candidates
    WHERE id IN ({})
    AND (profile_summary IS NULL OR profile_summary = ''
         OR sector IS NULL OR sector = '')
    AND is_duplicate = 0
'''.format(','.join('?'*len(all_ids))), list(all_ids))

rows = cur.fetchall()
print(f'재파싱 대상: {len(rows)}명')

for r in rows:
    cid = r["id"]
    name_kr = r["name_kr"]
    raw_text = r["raw_text"] or ""
    
    if len(raw_text) < 50:
        print(f"Skipping {name_kr} - raw_text too short")
        continue

    print(f"Parsing {name_kr}...")
    parsed = None
    for attempt in range(3):
        try:
            prompt = MEGA_PROMPT.replace("{text}", f"[파일명: {name_kr}]\n\n" + raw_text[:6000])
            res = model.generate_content(prompt)
            raw = res.text.replace("```json", "").replace("```", "").strip()
            parsed = json.loads(raw)
            break
        except Exception as e:
            print(e)
            time.sleep(2)
            
    if not parsed:
        print(f"Failed to parse {name_kr}")
        continue
        
    sector = parsed.get("sector", "미분류")
    summary = parsed.get("summary", "")
    careers = parsed.get("careers_json", [])
    current_company, total_years = calculate_career_stats(careers)
    
    # Update SQLite
    cur.execute('''
        UPDATE candidates 
        SET sector=?, profile_summary=?, total_years=? 
        WHERE id=?
    ''', (sector, summary, total_years, cid))
    conn.commit()
    
    # Update Neo4j
    with driver.session() as session:
        session.run("""
            MERGE (c:Candidate {id: $id})
            SET c.profile_summary = $summary,
                c.total_years = $total_years, 
                c.sector = $sector
        """, id=cid, summary=summary, total_years=total_years, sector=sector)
        
        for edge in parsed.get("neo4j_edges", []):
            act, skill, conf, ev = edge.get("action", ""), edge.get("skill", ""), float(edge.get("confidence", 0.5)), edge.get("evidence_span", "")
            if act and skill:
                session.run(f"""
                    MERGE (c:Candidate {{id: $id}})
                    MERGE (s:Skill {{name: $skill}})
                    MERGE (c)-[r:{act}]->(s)
                    SET r.confidence = $conf, r.evidence_span = $ev, r.source = 'v3_reparse'
                """, id=cid, skill=skill, conf=conf, ev=ev)
                
    print(f"  -> {name_kr} 업데이트 완료 (sector: {sector}, years: {total_years})")

conn.close()
