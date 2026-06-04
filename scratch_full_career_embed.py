import json, sqlite3, time, os
from neo4j import GraphDatabase
from openai import OpenAI
import numpy as np

secrets = json.load(open('secrets.json', encoding='utf-8'))
client = OpenAI(api_key=secrets['OPENAI_API_KEY'])
driver = GraphDatabase.driver(secrets['NEO4J_URI'],
    auth=(secrets['NEO4J_USERNAME'], secrets['NEO4J_PASSWORD']))

conn = sqlite3.connect('candidates.db')
cur = conn.cursor()

# 아직 career_embeddings 없는 후보자 전체
cur.execute("""
    SELECT id, name_kr, careers_json, profile_summary, sector, current_company
    FROM candidates
    WHERE is_duplicate = 0
    AND careers_json IS NOT NULL
    AND length(careers_json) > 30
""")
rows = cur.fetchall()
print(f'처리 대상: {len(rows)}명')

def build_career_text(career: dict, sector: str, company: str) -> str:
    c_company = career.get('company', '') or career.get('회사명', '')
    role = (career.get('role', '') or career.get('title', '') or 
            career.get('직책', '') or career.get('position', ''))
    period = (career.get('duration', '') or career.get('period', '') or 
              career.get('기간', ''))
    desc = (career.get('description', '') or career.get('tasks', '') or
            career.get('업무', '') or career.get('주요업무', '') or '')
    if isinstance(desc, list):
        desc = ' '.join(str(d) for d in desc)
    
    parts = [p for p in [sector, c_company, role, period, str(desc)[:400]] if p]
    return ' '.join(parts)[:800]

processed = 0
skipped = 0
errors = 0

with driver.session() as session:
    for row in rows:
        cid, name_kr, careers_json_str, summary, sector, cur_company = row
        
        # 이미 처리된 것 스킵
        r = session.run(
            "MATCH (c:Candidate {id: $cid}) RETURN c.has_career_embeddings as done",
            cid=cid)
        rec = r.single()
        if rec and rec['done'] == True:
            skipped += 1
            continue
        
        try:
            careers = json.loads(careers_json_str)
            if not isinstance(careers, list) or len(careers) == 0:
                skipped += 1
                continue
            
            # 최근 3개 경력
            recent = careers[:3]
            texts = [build_career_text(c, sector or '', cur_company or '') 
                     for c in recent]
            texts = [t for t in texts if len(t) > 20]
            
            if not texts:
                skipped += 1
                continue
            
            # 배치 임베딩 (최대 3개 한번에)
            resp = client.embeddings.create(
                model='text-embedding-3-small',
                input=texts
            )
            embeddings = [e.embedding for e in resp.data]
            embeddings_json = json.dumps(embeddings)
            
            # Neo4j 저장
            session.run("""
                MATCH (c:Candidate {id: $cid})
                SET c.career_embeddings_json = $emb_json,
                    c.has_career_embeddings = true
            """, cid=cid, emb_json=embeddings_json)
            
            processed += 1
            if processed % 100 == 0:
                print(f'진행: {processed}명 완료 / 스킵: {skipped}')
                time.sleep(0.5)  # API rate limit 방지
        
        except Exception as e:
            errors += 1
            if errors % 50 == 0:
                print(f'오류 {errors}건: {e}')
            continue

conn.close()
driver.close()
print(f'최종: 처리 {processed}명, 스킵 {skipped}명, 오류 {errors}명')
