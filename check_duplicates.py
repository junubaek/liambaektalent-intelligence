import sqlite3
import json
import sys
from collections import defaultdict

sys.stdout.reconfigure(encoding='utf-8')

conn = sqlite3.connect('candidates.db')
cur = conn.cursor()

# 이름 기준으로 그룹핑
cur.execute("""
    SELECT id, name_kr, email, current_company, created_at, is_duplicate
    FROM candidates
    WHERE name_kr IS NOT NULL AND name_kr != ''
    ORDER BY name_kr, created_at
""")
rows = cur.fetchall()

# 이름별 그룹핑
groups = defaultdict(list)
for row in rows:
    name = row[1].strip() if row[1] else ''
    if name:
        groups[name].append({
            'id': row[0],
            'email': row[2],
            'current_company': row[3],
            'created_at': row[4],
            'is_duplicate': row[5]
        })

# 중복 있는 그룹만 필터
duplicates = {name: records for name, records in groups.items() if len(records) > 1}

with open('check_duplicates_report.txt', 'w', encoding='utf-8') as f:
    f.write(f"=== 중복 후보자 현황 ===\n")
    f.write(f"전체 후보자 수: {len(rows)}\n")
    f.write(f"중복 이름 수: {len(duplicates)}\n")
    f.write(f"중복 레코드 수 (구버전 포함): {sum(len(v) for v in duplicates.values())}\n\n")

    for name, records in sorted(duplicates.items()):
        f.write(f"[{name}] {len(records)}개 레코드\n")
        for r in records:
            flag = " <- 구버전 마킹 예정" if r['is_duplicate'] == 0 and r != records[-1] else ""
            f.write(f"  ID: {r['id'][:8]}... | current: {r['current_company']} | created: {r['created_at']} | is_dup: {r['is_duplicate']}{flag}\n")
        f.write("\n")

conn.close()
print("Report generated: check_duplicates_report.txt")
