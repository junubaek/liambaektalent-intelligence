import sqlite3, sys
sys.stdout.reconfigure(encoding='utf-8')
conn = sqlite3.connect('candidates.db')
cur = conn.cursor()
cur.execute('UPDATE candidates SET is_duplicate = 1 WHERE name_kr = "이상헌"')
cur.execute('UPDATE candidates SET is_duplicate = 0, is_neo4j_synced = 0, is_pinecone_synced = 0 WHERE id = "898ea4e0-77d4-46d5-bf4d-c2d5b4a04741"')
conn.commit()
conn.close()
print('Lee Sang-heon master record switched.')
