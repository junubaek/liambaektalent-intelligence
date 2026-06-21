import sqlite3
import sys
sys.stdout.reconfigure(encoding='utf-8')

db_path = r"C:\Users\cazam\Downloads\이력서자동분석검색시스템\candidates.db"
conn = sqlite3.connect(db_path)
cur = conn.cursor()

# [작업 1] 비표준 sector 분포 확인
print("=== [작업 1] 비표준 직무 분야(Sector) 분포 (상위 30개) ===")
cur.execute("""
    SELECT sector, COUNT(*) FROM candidates 
    WHERE sector NOT IN (
      'Eng_SW','Eng_AI','Eng_Data','Eng_Embedded','Eng_HW','Eng_Semi',
      'Product','Finance','Marketing','Sales','HR','Strategy',
      'Operations','Legal','Healthcare'
    )
    AND sector IS NOT NULL AND sector != ''
    GROUP BY sector 
    ORDER BY COUNT(*) DESC
    LIMIT 30
""")
sectors = cur.fetchall()
for idx, (sec, cnt) in enumerate(sectors, 1):
    print(f"  [{idx}] {sec or 'None'}: {cnt}명")

# [작업 2] 이름 오염 59건 목록 조회
print("\n=== [작업 2] 이름 필드 오염 데이터 목록 (상위 50개) ===")
cur.execute("""
    SELECT id, name_kr, current_company FROM candidates 
    WHERE length(name_kr) > 10 
    OR name_kr LIKE '%개발%' 
    OR name_kr LIKE '%기획%'
    OR name_kr LIKE '%부문%'
    OR name_kr LIKE '%원본%'
    OR name_kr LIKE '%.pdf%'
    OR name_kr LIKE '%.docx%'
    LIMIT 50
""")
corrupted = cur.fetchall()
print(f"조회된 의심 데이터 수: {len(corrupted)}건")
print("-" * 60)
for idx, (cid, name, comp) in enumerate(corrupted, 1):
    print(f"  [{idx}] 이름: {name} | 회사: {comp or '미상'} | ID: {cid}")

conn.close()
