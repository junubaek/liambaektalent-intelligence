import json, sys, codecs
sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer)
s = json.load(open('secrets.json', encoding='utf-8'))
from neo4j import GraphDatabase
driver = GraphDatabase.driver(s['NEO4J_URI'], auth=(s['NEO4J_USERNAME'], s['NEO4J_PASSWORD']))
with driver.session() as sess:
    r = sess.run('MATCH (c:Candidate) RETURN c LIMIT 5')
    for row in r:
        node = dict(row['c'])
        print(node)
driver.close()
