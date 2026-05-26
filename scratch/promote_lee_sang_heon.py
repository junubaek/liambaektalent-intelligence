import sqlite3, sys
sys.stdout.reconfigure(encoding='utf-8')
conn = sqlite3.connect('candidates.db')
cur = conn.cursor()

# Promote GA/Procurement Expert (Grepp)
ga_id = 'db752f0f-0f1a-437c-a09d-43c20442ab7b'
cur.execute('''UPDATE candidates SET is_duplicate = 0, 
               is_neo4j_synced = 0, is_pinecone_synced = 0
               WHERE id = ?''', (ga_id,))
print(f"Promoted GA Expert: {ga_id}")

# Promote Bioinformatics Expert (KCTC)
bio_id = '55726c4a-4601-4ee9-87dc-581d15eda75e'
cur.execute('''UPDATE candidates SET is_duplicate = 0,
               is_neo4j_synced = 0, is_pinecone_synced = 0
               WHERE id = ?''', (bio_id,))
print(f"Promoted Bio Expert: {bio_id}")

conn.commit()
conn.close()
print('완료')
