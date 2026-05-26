import sqlite3, json, sys
sys.stdout.reconfigure(encoding='utf-8')
from neo4j import GraphDatabase

conn = sqlite3.connect('candidates.db')
cur = conn.cursor()
cur.execute('''SELECT id, name_kr, current_company, profile_summary, 
               length(raw_text) as rt_len, is_duplicate
               FROM candidates WHERE name_kr = '이상헌' ''')
rows = cur.fetchall()
print(f"--- SQLite 검색 결과 ({len(rows)}건) ---")
for row in rows:
    print(f"ID: {row[0]}")
    print(f"이름: {row[1]}, 회사: {row[2]}, 중복여부: {row[5]}")
    print(f"요약: {row[3][:100]}...")
    print(f"Raw Text 길이: {row[4]}")
    print("-" * 30)

if not rows:
    print("이상헌을 찾을 수 없습니다.")
    sys.exit()

# is_duplicate = 0인 항목의 ID 사용
target_id = next((r[0] for r in rows if r[5] == 0), rows[0][0])

conn.close()

try:
    secrets = json.load(open('secrets.json'))
    driver = GraphDatabase.driver(secrets['NEO4J_URI'], auth=(secrets['NEO4J_USERNAME'], secrets['NEO4J_PASSWORD']))
    with driver.session() as session:
        # Candidate 노드 존재 확인
        node = session.run('MATCH (c:Candidate {id: $cid}) RETURN c.name, c.company', cid=target_id).single()
        if node:
            print(f"\n--- Neo4j Candidate 노드 확인 ---")
            print(f"이름: {node['c.name']}, 회사: {node['c.company']}")
            
            # 스킬 확인
            skills = session.run('MATCH (c:Candidate {id: $cid})-[r]->(s:Skill) RETURN s.name, type(r)', cid=target_id).data()
            print(f'Neo4j 스킬: {len(skills)}개')
            for s in skills[:10]:
                print(f'  {s["s.name"]} ({s["type(r)"]})')
                
            # 다른 관계 확인 (예: Sector, Experience 등)
            rels = session.run('MATCH (c:Candidate {id: $cid})-[r]->(n) WHERE NOT n:Skill RETURN labels(n)[0] as label, count(*) as count', cid=target_id).data()
            if rels:
                print(f"\n기타 관계:")
                for r in rels:
                    print(f"  - {r['label']}: {r['count']}개")
        else:
            print(f"\nNeo4j에 ID {target_id}인 노드가 없습니다.")
    driver.close()
except Exception as e:
    print(f"\nNeo4j 오류: {e}")
