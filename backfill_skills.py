"""
Neo4j Skills Backfill v2 - with reconnection and resume support
"""
import json, sqlite3, time, sys, re
from openai import OpenAI
from neo4j import GraphDatabase

DB_PATH = r'C:\Users\cazam\Downloads\이력서자동분석검색시스템\candidates.db'
SECRETS_PATH = r'C:\Users\cazam\Downloads\이력서자동분석검색시스템\secrets.json'
GPT_MODEL = 'gpt-4.1-mini'
BATCH_LOG_EVERY = 50
PROGRESS_FILE = r'C:\Users\cazam\Downloads\이력서자동분석검색시스템\backfill_progress.json'

s = json.load(open(SECRETS_PATH, encoding='utf-8'))
openai_client = OpenAI(api_key=s['OPENAI_API_KEY'])

sys.path.insert(0, r'C:\Users\cazam\Downloads\이력서자동분석검색시스템')
from ontology_graph import CANONICAL_MAP
canonical_nodes = sorted(set(CANONICAL_MAP.values()))
canonical_list_str = ', '.join(canonical_nodes[:400])

VALID_ACTIONS = {'BUILT','DESIGNED','MANAGED','ANALYZED','LAUNCHED','NEGOTIATED','GREW','SUPPORTED'}

def get_driver():
    return GraphDatabase.driver(s['NEO4J_URI'], auth=(s['NEO4J_USERNAME'], s['NEO4J_PASSWORD']))

def run_with_retry(driver_ref, query, params=None, max_retries=3):
    for attempt in range(max_retries):
        try:
            with driver_ref[0].session() as sess:
                result = sess.run(query, params or {})
                return list(result)
        except Exception as e:
            print(f'  [RETRY {attempt+1}] Neo4j error: {e}')
            time.sleep(2)
            try:
                driver_ref[0].close()
            except:
                pass
            driver_ref[0] = get_driver()
    return []

def extract_skills(text, name):
    prompt = f"""You are a skill extractor for a Korean recruiting platform.
Extract professional skills from the resume text below.
Map each skill to the closest node from the STANDARD SKILL LIST.
If no match exists, create a Snake_Case name. NEVER use spaces in skill names.

STANDARD SKILL LIST: {canonical_list_str}

Valid verbs: BUILT, DESIGNED, MANAGED, ANALYZED, LAUNCHED, NEGOTIATED, GREW, SUPPORTED

Return ONLY valid JSON array:
[{{"action": "VERB", "skill": "Skill_Node", "confidence": 0.0-1.0}}]

Resume:
{text[:5000]}"""
    try:
        resp = openai_client.chat.completions.create(
            model=GPT_MODEL,
            messages=[{'role':'user','content':prompt}],
            temperature=0,
            max_tokens=2000
        )
        raw = resp.choices[0].message.content.strip()
        raw = re.sub(r'```json|```','', raw).strip()
        edges = json.loads(raw)
        result = []
        for e in edges:
            action = e.get('action','BUILT').upper()
            if action not in VALID_ACTIONS:
                action = 'BUILT'
            skill = e.get('skill','').replace(' ','_').strip()
            if not skill:
                continue
            skill_canon = CANONICAL_MAP.get(skill) or CANONICAL_MAP.get(skill.lower())
            if skill_canon:
                skill = skill_canon
            conf = float(e.get('confidence', 0.7))
            result.append({'action': action, 'skill': skill, 'confidence': conf})
        return result
    except Exception as ex:
        print(f'  [WARN] {name}: {ex}')
        return []

def main():
    driver_ref = [get_driver()]

    # 이미 완료된 ID 로드
    done_ids = set()
    try:
        prog = json.load(open(PROGRESS_FILE, encoding='utf-8'))
        done_ids = set(prog.get('done_ids', []))
        print(f'[RESUME] Already done: {len(done_ids)}')
    except:
        print('[START] Fresh run')

    print('[STEP 1] Finding zero-skill candidates in Neo4j...')
    rows_neo = run_with_retry(driver_ref, 'MATCH (c:Candidate) WHERE NOT (c)-[]->(:Skill) RETURN c.id as id')
    zero_ids = list(set(row['id'] for row in rows_neo if row['id']))
    print(f'  Zero-skill in Neo4j: {len(zero_ids)}')

    # 이미 완료된 것 제외
    remaining_ids = [cid for cid in zero_ids if cid not in done_ids]
    print(f'  Remaining to process: {len(remaining_ids)}')

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    placeholders = ','.join(['?' for _ in remaining_ids])
    if not remaining_ids:
        print('All done!')
        driver_ref[0].close()
        return
    cur.execute(f'''
        SELECT id, name_kr, sector, total_years, current_company, current_title, raw_text
        FROM candidates
        WHERE id IN ({placeholders}) AND is_duplicate=0
        AND raw_text IS NOT NULL AND length(raw_text) > 200
    ''', remaining_ids)
    rows = cur.fetchall()
    conn.close()
    print(f'  With raw_text: {len(rows)}')

    print('[STEP 2] Backfilling skills...')
    ok = 0
    skipped = 0
    for i, row in enumerate(rows):
        cid, name, sector, total_years, company, title, raw_text = row
        edges = extract_skills(raw_text, name or cid[:8])
        if edges:
            run_with_retry(driver_ref, '''
                MERGE (c:Candidate {id: $id})
                SET c.name=$name, c.sector=$sector,
                    c.total_years=$ty, c.current_company=$co, c.current_title=$ti
            ''', {'id':cid,'name':name or '','sector':sector or '','ty':total_years or 0,'co':company or '','ti':title or ''})
            for edge in edges:
                try:
                    action = edge['action']
                    run_with_retry(driver_ref, f'''
                        MERGE (c:Candidate {{id: $id}})
                        MERGE (s:Skill {{name: $skill}})
                        MERGE (c)-[r:{action}]->(s)
                        SET r.confidence=$conf
                    ''', {'id':cid,'skill':edge['skill'],'conf':edge['confidence']})
                except:
                    pass
            ok += 1
        else:
            skipped += 1

        done_ids.add(cid)

        # 진행상황 저장 (50명마다)
        if (i+1) % BATCH_LOG_EVERY == 0:
            print(f'  {i+1}/{len(rows)} | ok:{ok} skip:{skipped}')
            with open(PROGRESS_FILE, 'w', encoding='utf-8') as f:
                json.dump({'done_ids': list(done_ids)}, f)

        time.sleep(0.1)

    # 최종 저장
    with open(PROGRESS_FILE, 'w', encoding='utf-8') as f:
        json.dump({'done_ids': list(done_ids)}, f)

    print(f'\n[DONE] ok:{ok}, skipped:{skipped}')
    rows2 = run_with_retry(driver_ref, 'MATCH (c:Candidate) RETURN count(c) as n')
    rows3 = run_with_retry(driver_ref, 'MATCH (s:Skill) RETURN count(s) as n')
    rows4 = run_with_retry(driver_ref, 'MATCH ()-[e]->(:Skill) RETURN count(e) as n')
    rows5 = run_with_retry(driver_ref, 'MATCH (c:Candidate) WHERE NOT (c)-[]->(:Skill) RETURN count(c) as n')
    print(f'Candidates:{rows2[0]["n"]} Skills:{rows3[0]["n"]} Edges:{rows4[0]["n"]} StillZero:{rows5[0]["n"]}')
    driver_ref[0].close()

if __name__ == '__main__':
    main()
