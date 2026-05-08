import json
from neo4j import GraphDatabase

secrets = json.load(open('secrets.json', 'r', encoding='utf-8'))
driver = GraphDatabase.driver(secrets['NEO4J_URI'], auth=(secrets['NEO4J_USERNAME'], secrets['NEO4J_PASSWORD']))

with driver.session() as session:
    stats_query = '''
        MATCH (c:Candidate)
        OPTIONAL MATCH (c)-[r]->(s:Skill)
        WITH c, count(r) as skill_cnt
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
    print(f"With Skills: {with_skills} ({with_skills/total*100:.1f}%)")
    print(f"No Skills: {no_skills} ({no_skills/total*100:.1f}%)")
    print(f"Avg Skills: {avg_skills:.1f}")

    # Verb distribution
    rel_query = '''
        MATCH (c:Candidate)-[r]->(s:Skill)
        RETURN type(r) as rel, count(r) as cnt
        ORDER BY cnt DESC
    '''
    rels = session.run(rel_query).data()
    print("\nVerb Distribution:")
    for r in rels:
        print(f"  {r['rel']}: {r['cnt']}")

driver.close()
