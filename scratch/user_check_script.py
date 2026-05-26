import sqlite3, sys
sys.stdout.reconfigure(encoding='utf-8')
from neo4j import GraphDatabase

conn = sqlite3.connect('candidates.db')
cur = conn.cursor()
cur.execute('''SELECT id, name_kr, current_company, sector, profile_summary
               FROM candidates WHERE is_duplicate=0 AND is_neo4j_synced=0''')
rows = cur.fetchall()
print(f'동기화 대상: {len(rows)}명')

aura = GraphDatabase.driver('neo4j+s://deb21ee0.databases.neo4j.io',
       auth=('deb21ee0', 'pdaL-7EcG4TAejKf9HuSMkgiA0uPWP6Yl5Bw-XywhrQ'))
session = aura.session()

for i in range(0, len(rows), 100):
    batch = rows[i:i+100]
    data = [{'id':r[0],'name':r[1],'company':r[2],'sector':r[3],'summary':r[4]} for r in batch]
    session.run('''
        UNWIND $batch as r
        MERGE (c:Candidate {id: r.id})
        SET c.name_kr=r.name, c.current_company=r.company,
            c.sector=r.sector, c.summary=r.summary
    ''', batch=data)
    print(f'  {min(i+100,len(rows))}/{len(rows)} 완료')

cur.execute('UPDATE candidates SET is_neo4j_synced=1 WHERE is_duplicate=0 AND is_neo4j_synced=0')
conn.commit()
conn.close()
aura.close()
print('완료')
