import json, sys, codecs
sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer)
s = json.load(open('secrets.json', encoding='utf-8'))
from neo4j import GraphDatabase
driver = GraphDatabase.driver(s['NEO4J_URI'], auth=(s['NEO4J_USERNAME'], s['NEO4J_PASSWORD']))
with driver.session() as sess:
    r = sess.run('''
        MATCH (c:Candidate)
        WHERE c.name_kr IS NOT NULL AND c.name_kr <> ""
        RETURN c.id as id, c.name_kr as name_kr, c.current_title as title, 
               c.current_company as company, c.sector as sector
        LIMIT 5
    ''')
    for row in r:
        print(row['name_kr'], '|', row['title'], '|', row['company'], '|', row['sector'])
    
    r2 = sess.run('''
        MATCH (c:Candidate)
        WHERE c.name_kr IS NULL OR c.name_kr = ""
        RETURN count(c) as cnt
    ''')
    print('name_kr 없는 노드:', r2.single()['cnt'])
driver.close()
