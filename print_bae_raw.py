import sys, codecs, sqlite3
sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer)
conn = sqlite3.connect('candidates.db')
cur = conn.cursor()
cur.execute('SELECT raw_text FROM candidates WHERE id="028449d0-5ae4-46cf-b403-20f23e1e5fab"')
row = cur.fetchone()
if row and row[0]:
    print('Length:', len(row[0]))
    print(row[0])
conn.close()
