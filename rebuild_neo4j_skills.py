"""
Neo4j Skills Graph Rebuilder
- Neo4j의 모든 Candidate/Skill 노드 삭제 후 재구축
- SQLite raw_text → GPT-4.1-mini → CANONICAL_MAP 정규화 → Neo4j
- SQLite는 건드리지 않음
"""
import json, sqlite3, time, sys, re
from openai import OpenAI
from neo4j import GraphDatabase

# ── 설정 ──────────────────────────────────────────────────────────────
DB_PATH = r'C:\Users\cazam\Downloads\이력서자동분석검색시스템\candidates.db'
SECRETS_PATH = r'C:\Users\cazam\Downloads\이력서자동분석검색시스템\secrets.json'
GPT_MODEL = 'gpt-4.1-mini'
BATCH_LOG_EVERY = 50
# ──────────────────────────────────────────────────────────────────────

s = json.load(open(SECRETS_PATH, encoding='utf-8'))
openai_client = OpenAI(api_key=s['OPENAI_API_KEY'])
neo4j_driver = GraphDatabase.driver(s['NEO4J_URI'], auth=(s['NEO4J_USERNAME'], s['NEO4J_PASSWORD']))

# CANONICAL_MAP 로드
sys.path.insert(0, r'C:\Users\cazam\Downloads\이력서자동분석검색시스템')
from ontology_graph import CANONICAL_MAP
canonical_nodes = sorted(set(CANONICAL_MAP.values()))
canonical_list_str = ', '.join(canonical_nodes[:400])  # 프롬프트 길이 제한

SKILL_PROMPT = f"""You are a skill extractor for a Korean recruiting platform.
Extract professional skills from the resume text below.
Map each skill to the closest node from the STANDARD SKILL LIST.
If no match exists, create a Snake_Case name (e.g. New_Skill_Name).
NEVER use spaces in skill names.

STANDARD SKILL LIST (use these exact values when possible):
{canonical_list_str}

Valid action verbs: BUILT, DESIGNED, MANAGED, ANALYZED, LAUNCHED, NEGOTIATED, GREW, SUPPORTED

Return ONLY valid JSON array, no explanation:
[{{"action": "VERB", "skill": "Skill_Node", "confidence": 0.0-1.0}}]

Resume text:
{{text}}"""

VALID_ACTIONS = {'BUILT','DESIGNED','MANAGED','ANALYZED','LAUNCHED','NEGOTIATED','GREW','SUPPORTED'}

def extract_skills(text: str, name: str) -> list:
    prompt = SKILL_PROMPT.replace('{text}', text[:5000])
    try:
        resp = openai_client.chat.completions.create(
            model=GPT_MODEL,
            messages=[{'role':'user','content':prompt}],
            temperature=0,
            max_tokens=1500
        )
        raw = resp.choices[0].message.content.strip()
        raw = re.sub(r'```json|```','', raw).strip()
        edges = json.loads(raw)
        # 정규화
        result = []
        for e in edges:
            action = e.get('action','BUILT').upper()
            if action not in VALID_ACTIONS:
                action = 'BUILT'
            skill = e.get('skill','').replace(' ','_').strip()
            if not skill:
                continue
            # CANONICAL_MAP 재확인
            skill_canon = CANONICAL_MAP.get(skill) or CANONICAL_MAP.get(skill.lower())
            if skill_canon:
                skill = skill_canon
            conf = float(e.get('confidence', 0.7))
            result.append({'action': action, 'skill': skill, 'confidence': conf})
        return result
    except Exception as ex:
        print(f'  [WARN] GPT error for {name}: {ex}')
        return []

def rebuild_neo4j(candidates: list):
    print(f'\n[STEP 2] Rebuilding Neo4j for {len(candidates)} candidates...')
    with neo4j_driver.session() as sess:
        # 전체 삭제
        print('  Clearing Neo4j...')
        sess.run('MATCH (n) DETACH DELETE n')
        print('  Neo4j cleared.')

        ok = 0
        for i, c in enumerate(candidates):
            cid = c['id']
            name = c['name_kr'] or ''
            edges = c['edges']

            # Candidate 노드 생성
            sess.run("""
                MERGE (c:Candidate {id: $id})
                SET c.name = $name,
                    c.sector = $sector,
                    c.total_years = $total_years,
                    c.current_company = $company,
                    c.current_title = $title
            """, id=cid, name=name,
                sector=c.get('sector',''),
                total_years=c.get('total_years',0),
                company=c.get('current_company',''),
                title=c.get('current_title',''))

            # Skill 엣지 생성
            for edge in edges:
                action = edge['action']
                skill = edge['skill']
                conf = edge['confidence']
                try:
                    sess.run(f"""
                        MERGE (c:Candidate {{id: $id}})
                        MERGE (s:Skill {{name: $skill}})
                        MERGE (c)-[r:{action}]->(s)
                        SET r.confidence = $conf
                    """, id=cid, skill=skill, conf=conf)
                except Exception as ex:
                    pass

            ok += 1
            if ok % BATCH_LOG_EVERY == 0:
                print(f'  Neo4j sync: {ok}/{len(candidates)}')

    print(f'  Neo4j rebuild complete: {ok} candidates')

def main():
    # SQLite에서 active 후보자 로드
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        SELECT id, name_kr, sector, total_years, current_company, current_title, raw_text
        FROM candidates
        WHERE is_duplicate=0 AND raw_text IS NOT NULL AND length(raw_text) > 200
        ORDER BY created_at
    """)
    rows = cur.fetchall()
    conn.close()
    print(f'[STEP 1] Extracting skills for {len(rows)} candidates...')

    candidates = []
    errors = 0
    for i, row in enumerate(rows):
        cid, name, sector, total_years, company, title, raw_text = row
        edges = extract_skills(raw_text, name or cid[:8])
        candidates.append({
            'id': cid, 'name_kr': name, 'sector': sector,
            'total_years': total_years or 0,
            'current_company': company or '',
            'current_title': title or '',
            'edges': edges
        })
        if (i+1) % BATCH_LOG_EVERY == 0:
            print(f'  GPT extraction: {i+1}/{len(rows)} (last: {name}, edges: {len(edges)})')
        time.sleep(0.1)  # rate limit 방지

    print(f'  Extraction done. Total candidates: {len(candidates)}, errors: {errors}')

    # Neo4j 재구축
    rebuild_neo4j(candidates)

    # 최종 통계
    with neo4j_driver.session() as sess:
        cnt_c = sess.run('MATCH (c:Candidate) RETURN count(c) as cnt').single()['cnt']
        cnt_s = sess.run('MATCH (s:Skill) RETURN count(s) as cnt').single()['cnt']
        cnt_e = sess.run('MATCH ()-[e]->(:Skill) RETURN count(e) as cnt').single()['cnt']
        print(f'\n[DONE] Candidates: {cnt_c}, Skills: {cnt_s}, Edges: {cnt_e}')

    neo4j_driver.close()

if __name__ == '__main__':
    main()
