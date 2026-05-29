import json
import sqlite3
import sys
import time
import os
import google.generativeai as genai
from concurrent.futures import ThreadPoolExecutor, as_completed
from incremental_ingest_v10 import MEGA_PROMPT, calculate_career_stats
from neo4j import GraphDatabase

sys.stdout.reconfigure(encoding='utf-8')

# secrets.json에서 API 키 로드
secrets_path = r"C:\Users\cazam\Downloads\이력서자동분석검색시스템\secrets.json"
with open(secrets_path, "r", encoding="utf-8") as f:
    secrets = json.load(f)

genai.configure(api_key=secrets["GEMINI_API_KEY"])
model = genai.GenerativeModel("gemini-2.5-flash")

n_uri = secrets.get("NEO4J_URI")
n_user = secrets.get("NEO4J_USERNAME")
n_pw = secrets.get("NEO4J_PASSWORD")
driver = GraphDatabase.driver(n_uri, auth=(n_user, n_pw))

db_path = r"C:\Users\cazam\Downloads\이력서자동분석검색시스템\candidates.db"

conn = sqlite3.connect(db_path)
cur = conn.cursor()

# 342명의 껍데기 경력 후보자 찾기 (careers_json이 null 혹은 [] 이면서 raw_text가 충분히 존재하는 경우)
cur.execute('''
    SELECT id, name_kr, raw_text, sector, current_company
    FROM candidates
    WHERE (careers_json IS NULL OR careers_json = '[]' OR careers_json = '')
      AND raw_text IS NOT NULL AND length(raw_text) > 200
''')
rows = cur.fetchall()
conn.close()

print(f"Purification Target: {len(rows)} candidates")

def reparse_one(r):
    cid = r[0]
    name_kr = r[1]
    raw_text = r[2] or ""
    old_sector = r[3]
    
    parsed = None
    for attempt in range(3):
        try:
            prompt = MEGA_PROMPT.replace("{text}", f"[파일명: {name_kr}]\n\n" + raw_text[:6000])
            res = model.generate_content(prompt)
            raw = res.text.replace("```json", "").replace("```", "").strip()
            parsed = json.loads(raw)
            break
        except Exception as e:
            time.sleep(1.5)
            
    if not parsed:
        return cid, name_kr, False, "parsing failed", None, None, None, None, None, None
        
    sector = parsed.get("sector", old_sector)
    summary = parsed.get("summary", "")
    careers = parsed.get("careers_json", [])
    edu = parsed.get("education_json", [])
    neo4j_edges = parsed.get("neo4j_edges", [])
    
    # Calculate stats
    current_company, total_years = calculate_career_stats(careers)
    
    return cid, name_kr, True, "", sector, summary, careers, edu, current_company, total_years, neo4j_edges

success_cnt = 0
failed_cnt = 0
updates = []
neo4j_updates = []

print("Starting LLM Career Purification Parallel Pipeline...")
with ThreadPoolExecutor(max_workers=30) as executor:
    futures = [executor.submit(reparse_one, r) for r in rows]
    for idx, future in enumerate(as_completed(futures), 1):
        res = future.result()
        if res[2]: # success
            cid, name_kr, _, _, sector, summary, careers, edu, current_company, total_years, neo4j_edges = res
            updates.append((
                json.dumps(careers, ensure_ascii=False),
                json.dumps(edu, ensure_ascii=False),
                summary,
                sector,
                total_years,
                current_company,
                cid
            ))
            neo4j_updates.append((cid, name_kr, current_company, summary, total_years, sector, neo4j_edges))
            success_cnt += 1
            print(f"[{idx}/{len(rows)}] Success: {name_kr} -> {current_company} ({total_years} yrs)")
        else:
            cid, name_kr, _, msg, *rest = res
            failed_cnt += 1
            print(f"[{idx}/{len(rows)}] Failed: {name_kr} ({msg})")

# SQLite 일괄 업데이트
if updates:
    print("\nUpdating SQLite Database...")
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.executemany('''
        UPDATE candidates 
        SET careers_json = ?, education_json = ?, profile_summary = ?, sector = ?, total_years = ?, current_company = ?, is_parsed = 1
        WHERE id = ?
    ''', updates)
    conn.commit()
    conn.close()
    print("SQLite Database successfully updated.")

# Neo4j 그래프 일괄 업데이트
if neo4j_updates:
    print("\nUpdating Neo4j Graph Database...")
    try:
        with driver.session() as session:
            for cid, name_kr, current_company, summary, total_years, sector, neo4j_edges in neo4j_updates:
                # 1. Update Candidate Node
                session.run("""
                    MERGE (c:Candidate {id: $id})
                    SET c.name = $name_kr, c.current_company = $current_company,
                        c.profile_summary = $summary, c.total_years = $total_years, c.sector = $sector
                """, id=cid, name_kr=name_kr, current_company=current_company, summary=summary, total_years=total_years, sector=sector)
                
                # 2. Re-sync edges
                for edge in neo4j_edges:
                    act, skill = edge.get("action", ""), edge.get("skill", "")
                    conf = float(edge.get("confidence", 0.5))
                    ev = edge.get("evidence_span", "")
                    if act and skill:
                        session.run(f"""
                            MERGE (c:Candidate {{id: $id}})
                            MERGE (s:Skill {{name: $skill}})
                            MERGE (c)-[r:{act}]->(s)
                            SET r.confidence = $conf, r.evidence_span = $ev, r.source = 'purify_careers'
                        """, id=cid, skill=skill, conf=conf, ev=ev)
        print("Neo4j Graph Database successfully updated.")
    except Exception as e:
        print(f"Neo4j Update Error: {e}")

driver.close()
print(f"\nPurification complete! Success: {success_cnt} candidates | Failed: {failed_cnt} candidates.")
