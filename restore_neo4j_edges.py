import sqlite3, json, sys
sys.stdout.reconfigure(encoding='utf-8')
from neo4j import GraphDatabase

secrets = json.load(open('secrets.json', encoding='utf-8'))
driver = GraphDatabase.driver(secrets['NEO4J_URI'], auth=(secrets['NEO4J_USERNAME'], secrets['NEO4J_PASSWORD']))
session = driver.session()

# 현재 엣지 수
before = session.run('MATCH ()-[r:BUILT|DESIGNED|MANAGED|ANALYZED|LED|LAUNCHED|GREW|NEGOTIATED|SUPPORTED]->() RETURN count(r)').single()[0]
print(f'복구 전 엣지: {before}개')

conn = sqlite3.connect('candidates.db')
cur = conn.cursor()
cur.execute('''SELECT id, parsed_career_json FROM candidates
               WHERE is_duplicate=0 AND parsed_career_json IS NOT NULL
               AND parsed_career_json != '' AND parsed_career_json != '[]' ''')
rows = cur.fetchall()
print(f'처리 대상: {len(rows)}명')

ACTION_TYPES = ['BUILT','DESIGNED','MANAGED','ANALYZED','LED','LAUNCHED','GREW','NEGOTIATED','SUPPORTED']

total_edges = 0
for i, (cid, career_json) in enumerate(rows):
    try:
        careers = json.loads(career_json)
        if not isinstance(careers, list): continue
        
        for career in careers:
            action = career.get('action', '').upper()
            skills = career.get('skills', [])
            if action not in ACTION_TYPES or not skills: continue
            
            for skill in skills:
                if not skill: continue
                session.run(f'''
                    MATCH (c:Candidate {{id: $cid}})
                    MERGE (s:Skill {{name: $skill}})
                    MERGE (c)-[:{action}]->(s)
                ''', cid=cid, skill=skill)
                total_edges += 1
    except Exception as e:
        continue
    
    if (i+1) % 100 == 0:
        print(f'  {i+1}/{len(rows)} 처리 중... 엣지 {total_edges}개')

conn.close()

after = session.run('MATCH ()-[r:BUILT|DESIGNED|MANAGED|ANALYZED|LED|LAUNCHED|GREW|NEGOTIATED|SUPPORTED]->() RETURN count(r)').single()[0]
print(f'복구 후 엣지: {after}개')
driver.close()
print('완료')
