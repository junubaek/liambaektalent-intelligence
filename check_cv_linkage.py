import sqlite3
import json
import sys
sys.stdout.reconfigure(encoding='utf-8')

conn = sqlite3.connect('candidates.db')
cur = conn.cursor()

targets = ['홍주영', '정한아', '이민지', '정소윤', '권슬기', '김승현', '강해나', '장현', '성장현', '김현정', '손민정', '김광우', '조예원', '남현승']

print("=== 후보자 상태 및 Google Drive URL 확인 ===\n")
for name in targets:
    cur.execute("""
        SELECT id, name_kr, current_company, sector, google_drive_url, is_duplicate, is_parsed
        FROM candidates
        WHERE name_kr LIKE ?
        ORDER BY is_duplicate ASC
    """, (f'%{name}%',))
    rows = cur.fetchall()
    
    if not rows:
        print(f"[{name}] ❌ 데이터 없음")
        continue

    for r in rows:
        cid, nm, company, sector, drive_url, is_dup, is_parsed = r
        master = "✅ 마스터" if is_dup == 0 else "❌ 중복"
        print(f"[{nm}] {master}")
        print(f"  ID: {cid[:8]}...")
        print(f"  Company : {company}")
        print(f"  Sector  : {sector}")
        print(f"  Drive   : {'연결됨' if drive_url else '❌ 미연결'}")
        print(f"  Parsed  : {is_parsed}")
        if drive_url:
            print(f"  URL     : {drive_url}")
        print()

conn.close()
