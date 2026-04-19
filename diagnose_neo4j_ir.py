import sqlite3
from neo4j import GraphDatabase

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

names = list(set([r[0] for r in rows if r[0]]))

uri = 'neo4j://127.0.0.1:7687'
auth = ('neo4j', 'toss1234')
driver = GraphDatabase.driver(uri, auth=auth)
with driver.session() as session:
    res = session.run("""
        UNWIND $names AS n
        MATCH (c:Candidate)
        WHERE c.name = n OR c.name CONTAINS n
        MATCH (c)-[r]->(s:Skill)
        RETURN s.name as skill_name, count(r) as cnt
        ORDER BY cnt DESC
        LIMIT 20
    """, names=names)
    print('--- SKILLS for 161 TARGET CANDIDATES ---')
    total = 0
    for record in res:
        print(f"{record['skill_name']}: {record['cnt']} edges")
        total += record['cnt']
    if total == 0:
        print('(No edges at all)')
        
    res2 = session.run("""
        UNWIND $names AS n
        MATCH (c:Candidate)
        WHERE c.name = n OR c.name CONTAINS n
        OPTIONAL MATCH (c)-[r]->(:Skill)
        WITH c, count(r) as eco
        RETURN SUM(CASE WHEN eco=0 THEN 1 ELSE 0 END) as zero_cands, count(c) as total_cands
    """, names=names)
    rec2 = res2.single()
    print('--- CANDIDATE COVERAGE ---')
    print(f"Total matched in Neo4j out of 161: {rec2['total_cands']}")
    print(f"Zero edge candidates: {rec2['zero_cands']}")
