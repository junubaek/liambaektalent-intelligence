import sqlite3
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')
ROOT_DIR = r"c:\Users\cazam\Downloads\이력서자동분석검색시스템"
DB_FILE = os.path.join(ROOT_DIR, "candidates.db")

conn = sqlite3.connect(DB_FILE)
conn.row_factory = sqlite3.Row
cur = conn.cursor()

stop_words = "('자금', '기획', '개발', '운영', '마케팅', '재무', '회계', '전략', '인사', '총무', '법무')"
query = f"SELECT id, name_kr FROM candidates WHERE is_duplicate=0 AND (name_kr IN {stop_words} OR length(name_kr) > 10)"

cur.execute(query)
for row in cur.fetchall():
    print(f"ID: {row['id']} | Name: {row['name_kr']}")

conn.close()
