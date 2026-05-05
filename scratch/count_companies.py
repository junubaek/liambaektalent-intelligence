import sys, sqlite3
import os

# Set output encoding to utf-8
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

db_path = 'candidates.db'
if not os.path.exists(db_path):
    print(f"Error: {db_path} not found.")
    sys.exit(1)

conn = sqlite3.connect(db_path)
cur = conn.cursor()

# Top 50 companies
cur.execute('''
    SELECT current_company, COUNT(*) as cnt
    FROM candidates
    WHERE current_company IS NOT NULL
    AND current_company != ''
    AND current_company != '미상'
    GROUP BY current_company
    ORDER BY cnt DESC
    LIMIT 50
''')
rows = cur.fetchall()

# Total unique companies
cur.execute('''
    SELECT COUNT(DISTINCT current_company)
    FROM candidates
    WHERE current_company IS NOT NULL
    AND current_company != ''
    AND current_company != '미상'
''')
total_unique = cur.fetchone()[0]

conn.close()

print(f'총 고유 회사 수: {total_unique}')
print("-" * 30)
for company, cnt in rows:
    print(f'{cnt:4d}명 | {company}')
