import json, sqlite3
s = json.load(open('secrets.json', encoding='utf-8'))
from neo4j import GraphDatabase
driver = GraphDatabase.driver(s['NEO4J_URI'], auth=(s['NEO4J_USERNAME'], s['NEO4J_PASSWORD']))

conn = sqlite3.connect('candidates.db')
cur = conn.cursor()
cur.execute('SELECT id, name_kr, current_title, current_company FROM candidates WHERE is_duplicate=0')
rows = cur.fetchall()
conn.close()

BATCH = 500
updated = 0
for i in range(0, len(rows), BATCH):
    batch = rows[i:i+BATCH]
    with driver.session() as sess:
        sess.run('''
            UNWIND $rows AS row
            MATCH (c:Candidate {id: row.id})
            SET c.name_kr = row.name_kr,
                c.current_title = row.current_title,
                c.current_company = row.current_company
        ''', rows=[{'id': r[0], 'name_kr': r[1] or '', 'current_title': r[2] or '', 'current_company': r[3] or ''} for r in batch])
    updated += len(batch)
    print(f'Updated: {updated}/{len(rows)}')

driver.close()
print('Done.')
