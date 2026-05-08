import json
from neo4j import GraphDatabase

secrets = json.load(open('secrets.json', 'r', encoding='utf-8'))
driver = GraphDatabase.driver(secrets['NEO4J_URI'], auth=(secrets['NEO4J_USERNAME'], secrets['NEO4J_PASSWORD']))

with driver.session() as session:
    # 2단계 연결까지 고려한 통계 (직접 연결 OR Experience_Chunk를 통한 연결)
    stats_query = '''
        MATCH (c:Candidate)
        OPTIONAL MATCH (c)-[r1:HAS_EXPERIENCE]->(e:Experience_Chunk)-[r2]->(s:Skill)
        OPTIONAL MATCH (c)-[r3]->(s2:Skill)
        WITH c, count(r2) + count(r3) as skill_cnt
        RETURN
            count(c) as total,
            sum(CASE WHEN skill_cnt > 0 THEN 1 ELSE 0 END) as with_skills,
            sum(CASE WHEN skill_cnt = 0 THEN 1 ELSE 0 END) as no_skills,
            avg(skill_cnt) as avg_skills
    '''
    stats = session.run(stats_query).single()

    total = stats['total']
    with_skills = stats['with_skills']
    no_skills = stats['no_skills']
    avg_skills = stats['avg_skills']

    print(f"Total Nodes: {total}")
    print(f"With Skills (1-hop or 2-hop): {with_skills} ({with_skills/total*100:.1f}%)")
    print(f"No Skills: {no_skills} ({no_skills/total*100:.1f}%)")
    print(f"Avg Skills: {avg_skills:.1f}")

    # Verb distribution (including 2-hop)
    rel_query = '''
        MATCH (n)-[r]->(s:Skill)
        WHERE n:Candidate OR n:Experience_Chunk
        RETURN type(r) as rel, count(r) as cnt
        ORDER BY cnt DESC
    '''
    rels = session.run(rel_query).data()
    print("\nVerb Distribution (All):")
    for r in rels:
        print(f"  {r['rel']}: {r['cnt']}")

driver.close()
