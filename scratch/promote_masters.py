import sqlite3, json, sys
sys.stdout.reconfigure(encoding='utf-8')
conn = sqlite3.connect('candidates.db')
cur = conn.cursor()

for name in ['김대중', '정윤오', '정예린']:
    cur.execute('''
        SELECT id, careers_json, profile_summary, raw_text
        FROM candidates WHERE name_kr = ?
        ORDER BY length(COALESCE(raw_text,"")) DESC
    ''', (name,))
    rows = cur.fetchall()
    if not rows:
        print(f'{name}: 없음')
        continue
    best_id = rows[0][0]
    cur.execute('UPDATE candidates SET is_duplicate = 1 WHERE name_kr = ?', (name,))
    cur.execute('UPDATE candidates SET is_duplicate = 0, is_neo4j_synced = 0, is_pinecone_synced = 0 WHERE id = ?', (best_id,))
    conn.commit()
    print(f'{name}: {best_id[:8]}... 마스터 승격 완료')

conn.close()
