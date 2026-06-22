import json
from neo4j import GraphDatabase

s = json.load(open('secrets.json', encoding='utf-8'))
driver = GraphDatabase.driver(s['NEO4J_URI'], auth=(s['NEO4J_USERNAME'], s['NEO4J_PASSWORD']))

with driver.session() as sess:
    result = sess.run("""
        MATCH ()-[e]->(s:Skill)
        WHERE s.name CONTAINS ' '
        RETURN s.name as skill, count(e) as cnt
        ORDER BY cnt DESC LIMIT 200
    """)
    skills = [(r['skill'], r['cnt']) for r in result]

driver.close()

with open('unmapped_skills_top200.json', 'w', encoding='utf-8') as f:
    json.dump(skills, f, ensure_ascii=False, indent=2)

print(f'Saved {len(skills)} skills')
for s, c in skills[:30]:
    print(f'{c:4d} {s}')
