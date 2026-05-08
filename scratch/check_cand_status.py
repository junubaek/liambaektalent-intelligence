import sqlite3

conn = sqlite3.connect('candidates.db')
cur = conn.cursor()
names = ["이신형", "이상헌", "배유정", "김대중", "최우성"]

for name in names:
    cur.execute('SELECT id, name_kr, length(raw_text), is_parsed, is_neo4j_synced FROM candidates WHERE name_kr = ?', (name,))
    rows = cur.fetchall()
    print(f"Name: {name}")
    for r in rows:
        print(f"  - ID: {r[0]} | Text Length: {r[2]} | Parsed: {r[3]} | Synced: {r[4]}")

conn.close()
