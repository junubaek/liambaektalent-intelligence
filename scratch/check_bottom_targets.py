import sqlite3
import json

conn = sqlite3.connect('candidates.db')
cur = conn.cursor()

# 하위 5개 쿼리 타겟 정보
targets = [
    ("최우성", "c3d4ee55-266a-44f6-8e66-fb7486be38a8"),
    ("이영도", "8e4b53e0-5f55-41d7-a311-c43d9727c516"),
    ("김정수", "c1351abe-4809-483d-97b6-291718d2ce1d"),
    ("조재영", "32022567-1b6f-8152-9c8d-c4f8079c01b8"),
    ("김정기", "32e22567-1b6f-8101-ab31-c33a53561a96")
]

import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

print("--- Checking Bottom Query Targets in SQLite ---")
for name, cid in targets:
    cur.execute("SELECT id, name_kr FROM candidates WHERE id = ?", (cid,))
    row = cur.fetchone()
    if row:
        print(f"FOUND: {row[1]} ({row[0]})")
    else:
        # 이름으로 검색 시도
        cur.execute("SELECT id, name_kr FROM candidates WHERE name_kr = ?", (name,))
        rows = cur.fetchall()
        if rows:
            print(f"ID MISMATCH: {name} (Expected {cid}, but DB has {[r[0] for r in rows]})")
        else:
            print(f"NOT FOUND: {name} ({cid})")

conn.close()
