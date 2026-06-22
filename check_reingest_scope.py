import sqlite3, sys, codecs
sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer)
conn = sqlite3.connect('candidates.db')
cur = conn.cursor()

cur.execute("SELECT COUNT(*) FROM candidates WHERE is_duplicate=0")
total = cur.fetchone()[0]
print('Total active:', total)

cur.execute("SELECT COUNT(*) FROM candidates WHERE is_duplicate=0 AND raw_text IS NOT NULL AND length(raw_text) > 200")
has_text = cur.fetchone()[0]
print('Has sufficient raw_text:', has_text)

cur.execute("SELECT COUNT(*) FROM candidates WHERE is_duplicate=0 AND (raw_text IS NULL OR length(raw_text) <= 200)")
no_text = cur.fetchone()[0]
print('No/short raw_text:', no_text)

cur.execute("SELECT AVG(length(raw_text)) FROM candidates WHERE is_duplicate=0 AND raw_text IS NOT NULL")
avg_len = cur.fetchone()[0]
print(f'Avg raw_text length: {avg_len:.0f} chars')

conn.close()
