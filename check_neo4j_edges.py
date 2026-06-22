import sqlite3, json, sys, codecs
sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer)
conn = sqlite3.connect('candidates.db')
cur = conn.cursor()

# cei_json에 neo4j_edges가 있는지 확인
cur.execute("""
    SELECT id, name_kr, cei_json 
    FROM candidates 
    WHERE is_duplicate=0 AND cei_json IS NOT NULL AND cei_json != ''
    LIMIT 3
""")
for r in cur.fetchall():
    print(r[1], r[0][:8])
    try:
        d = json.loads(r[2])
        print('  cei_json keys:', list(d.keys())[:10])
        if 'neo4j_edges' in d:
            print('  neo4j_edges count:', len(d['neo4j_edges']))
            print('  sample:', d['neo4j_edges'][:2])
    except:
        print('  parse error')

# company_timeline에 스킬 있는지 확인  
cur.execute("""
    SELECT id, name_kr, company_timeline
    FROM candidates
    WHERE is_duplicate=0 AND company_timeline IS NOT NULL AND company_timeline != ''
    LIMIT 2
""")
print('\n=== company_timeline sample ===')
for r in cur.fetchall():
    print(r[1], r[0][:8])
    try:
        d = json.loads(r[2])
        print('  keys:', list(d[0].keys()) if isinstance(d, list) else list(d.keys()))
    except:
        print('  raw:', str(r[2])[:100])

conn.close()
