import sqlite3, sys, os
sys.stdout.reconfigure(encoding='utf-8')
# Path to the candidates.db in this project
db_path = r"C:/Users/cazam/Downloads/이력서자동분석검색시스템/candidates.db"
conn = sqlite3.connect(db_path)
cur = conn.cursor()

# Count rows with source_file set
cur.execute("SELECT COUNT(*) FROM candidates WHERE source_file IS NOT NULL AND source_file != ''")
print('source_file 있음:', cur.fetchone()[0])

# Count rows without source_file
cur.execute("SELECT COUNT(*) FROM candidates WHERE source_file IS NULL OR source_file = ''")
print('source_file 없음:', cur.fetchone()[0])

# Sample 10 rows with source_file
cur.execute("""
    SELECT name_kr, source_file FROM candidates
    WHERE source_file IS NOT NULL AND source_file != ''
    LIMIT 10
""")
print('\nsource_file 샘플:')
for r in cur.fetchall():
    print(f'  {r[0]} | {r[1]}')

conn.close()
