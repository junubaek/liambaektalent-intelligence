import sqlite3
import sys
import json
sys.stdout.reconfigure(encoding='utf-8')

db_path = r"C:\Users\cazam\Downloads\이력서자동분석검색시스템\candidates.db"
conn = sqlite3.connect(db_path)
cur = conn.cursor()

# [1] 이정수 sector 수정
cur.execute("""
    UPDATE candidates 
    SET sector = 'Eng_SW' 
    WHERE name_kr = '이정수' AND current_company LIKE '%아프리카%'
""")
conn.commit()
rows_affected = cur.rowcount
print(f"[1] 이정수 후보자 Sector 수정 완료 (영향을 받은 행 수: {rows_affected}개)")

# [2] 같은 패턴으로 잘못 분류됐을 가능성 있는 케이스 확인
cur.execute("""
    SELECT name_kr, sector, current_company, profile_summary
    FROM candidates
    WHERE sector = 'Eng_Embedded'
    AND (
        profile_summary LIKE '%인프라 운영%'
        OR profile_summary LIKE '%CDN%'
        OR profile_summary LIKE '%미디어 서비스%'
        OR profile_summary LIKE '%서버 운영%'
        OR profile_summary LIKE '%클라우드 운영%'
    )
""")
rows = cur.fetchall()

print(f"\n[2] 잘못 분류되었을 가능성이 높은 유사 케이스 조회 결과 (총 {len(rows)}건):")
print("=" * 60)
for idx, r in enumerate(rows, 1):
    print(f"[{idx}] 이름: {r[0]}")
    print(f"    현재 분야: {r[1]}")
    print(f"    현재 회사: {r[2]}")
    print(f"    요약: {r[3]}")
    print("-" * 60)

conn.close()
