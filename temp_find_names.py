import sqlite3
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')
ROOT_DIR = r"c:\Users\cazam\Downloads\이력서자동분석검색시스템"
DB_FILE = os.path.join(ROOT_DIR, "candidates.db")

conn = sqlite3.connect(DB_FILE)
conn.row_factory = sqlite3.Row
cur = conn.cursor()

# Find dirty names logic: > 5 chars, symbols, or common stop words in names
query = """
SELECT id, name_kr
FROM candidates
WHERE is_duplicate=0
AND (
    length(name_kr) > 5
    OR name_kr LIKE '%대리%'
    OR name_kr LIKE '%과장%'
    OR name_kr LIKE '%팀장%'
    OR name_kr LIKE '%(%/%'
    OR name_kr LIKE '%관리%'
    OR name_kr LIKE '%엔지니어%'
)
LIMIT 10
"""
cur.execute(query)
for row in cur.fetchall():
    print(f"{row['id']} | {row['name_kr']}")

conn.close()
