import sqlite3
conn = sqlite3.connect('candidates.db')
cur = conn.cursor()
cur.execute('UPDATE candidates SET is_neo4j_synced = 0, is_pinecone_synced = 0 WHERE name_kr = "최우성" AND is_duplicate = 0')
conn.commit()
conn.close()
print('Choi Woo-sung sync flags reset.')
