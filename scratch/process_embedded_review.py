import sqlite3
import sys
import os
sys.stdout.reconfigure(encoding='utf-8')

db_path = r"C:\Users\cazam\Downloads\이력서자동분석검색시스템\candidates.db"
conn = sqlite3.connect(db_path)
cur = conn.cursor()

# [1] 박재국 sector 수정
cur.execute("""
    UPDATE candidates 
    SET sector = 'Eng_SW' 
    WHERE name_kr = '박재국' AND current_company LIKE '%SolarEdge%'
""")
conn.commit()
rows_affected = cur.rowcount
print(f"[1] 박재국 후보자 Sector 수정 완료 (영향을 받은 행 수: {rows_affected}개)")

# [2] Eng_Embedded 전체 목록 조회 및 파일 저장
cur.execute("""
    SELECT name_kr, current_company, profile_summary
    FROM candidates
    WHERE sector = 'Eng_Embedded'
    ORDER BY name_kr
""")
rows = cur.fetchall()
print(f"[2] Eng_Embedded 총 후보자 수: {len(rows)}명")

# scratch 디렉토리 확인 및 파일 쓰기
output_dir = r"C:\Users\cazam\Downloads\이력서자동분석검색시스템\scratch"
os.makedirs(output_dir, exist_ok=True)
output_path = os.path.join(output_dir, "eng_embedded_review.txt")

with open(output_path, "w", encoding="utf-8") as f:
    f.write(f"=== Eng_Embedded Candidates Profile Review ({len(rows)}명) ===\n")
    f.write("이 파일은 Eng_Embedded 직무 분류 후보자 전체의 프로필 요약 파일입니다. 직접 오분류 여부를 판단하실 수 있습니다.\n")
    f.write("=" * 80 + "\n\n")
    
    for idx, r in enumerate(rows, 1):
        name_kr, current_company, profile_summary = r
        f.write(f"[{idx}] 이름: {name_kr if name_kr else '미상'}\n")
        f.write(f"    현재 회사: {current_company if current_company else '미상'}\n")
        f.write(f"    프로필 요약: {profile_summary if profile_summary else '내용 없음'}\n")
        f.write("-" * 80 + "\n\n")

print(f"결과가 다음 경로에 성공적으로 저장되었습니다: {output_path}")

conn.close()
