import sqlite3
from neo4j import GraphDatabase
import traceback

def run_diagnostic():
    conn = sqlite3.connect('C:/Users/cazam/Downloads/이력서자동분석검색시스템/candidates.db')
    c = conn.cursor()
    c.execute("""
        SELECT name_kr FROM candidates
        WHERE raw_text LIKE '%IR%'
           OR raw_text LIKE '%투자자관계%'
           OR raw_text LIKE '%Investor Relations%'
    """)
    rows = c.fetchall()
    conn.close()

    names = set([r[0] for r in rows if r[0]])
    print(f'✅ SQLite에서 추출된 IR 포함 후보자 수 (고유 이름 기준): {len(names)}명')

    uri = 'neo4j://127.0.0.1:7687'
    auth = ('neo4j', 'toss1234')

    try:
        driver = GraphDatabase.driver(uri, auth=auth)
        with driver.session() as session:
            result = session.run("""
                MATCH (c:Candidate)-[r]->(s:Skill)
                RETURN c.name_kr AS name_kr, c.id AS cid, s.name as skill_name
            """)
            
            edges = []
            for record in result:
                edges.append({
                    'name_kr': record.get('name_kr'),
                    'cid': record.get('cid'),
                    'skill_name': record['skill_name']
                })
                
            print(f'Total edges in neo4j constraint to filter: {len(edges)}')
            
            matched_candidates_edges = {}
            matched_neo4j_candidates = set()
            
            for e in edges:
                c_name_kr = e['name_kr']
                cid = e['cid']
                
                name_matched = False
                if c_name_kr and c_name_kr in names:
                    name_matched = True
                elif cid:
                    for n in names:
                        if cid.startswith(n):
                            name_matched = True
                            break
                            
                if name_matched:
                    identifier = cid if cid else c_name_kr
                    matched_neo4j_candidates.add(identifier)
                    if identifier not in matched_candidates_edges:
                        matched_candidates_edges[identifier] = []
                    matched_candidates_edges[identifier].append(e['skill_name'])
                    
            res_cands = session.run("MATCH (c:Candidate) RETURN c.name_kr as name_kr, c.id as cid")
            all_neo4j = set()
            for rec in res_cands:
                c_name_kr = rec['name_kr']
                cid = rec['cid']
                if c_name_kr and c_name_kr in names:
                    all_neo4j.add(cid if cid else c_name_kr)
                elif cid:
                    for n in names:
                        if cid.startswith(n):
                             all_neo4j.add(cid)
                             break
                             
            print(f'\n📈 [엣지 및 노드 누락 현황]')
            print(f' - Neo4j에 노드(Candidate)로 검색된 사람 (해당 이름 패턴): {len(all_neo4j)}')
            
            zero_edge_count = len(all_neo4j) - len(matched_candidates_edges)
            print(f' - 이 중 엣지가 하나도 없는 0개인 사람: {zero_edge_count}명')
            
            skill_counts = {}
            for k, lst in matched_candidates_edges.items():
                for s in lst:
                    skill_counts[s] = skill_counts.get(s, 0) + 1
                    
            sorted_skills = sorted(skill_counts.items(), key=lambda x: -x[1])
            
            print('\n📊 [Top 20 매핑 노드 현황 (IR텍스트 보유자들 기준)]')
            for k, v in sorted_skills[:20]:
                print(f' - {k}: {v}개')

    except Exception as e:
        traceback.print_exc()

run_diagnostic()
