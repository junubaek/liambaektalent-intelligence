import json, sys, codecs
sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer)
s = json.load(open('secrets.json', encoding='utf-8'))
from neo4j import GraphDatabase
driver = GraphDatabase.driver(s['NEO4J_URI'], auth=(s['NEO4J_USERNAME'], s['NEO4J_PASSWORD']))
with driver.session() as sess:
    r = sess.run('''
        MATCH (c:Candidate {id: "028449d0-5ae4-46cf-b403-20f23e1e5fab"})-[e]->(s:Skill)
        RETURN type(e) as rel, s.name as skill
    ''')
    rows = list(r)
    print("배유정 skills:", len(rows))
    for row in rows:
        print(" ", row["rel"], "->", row["skill"])
driver.close()
