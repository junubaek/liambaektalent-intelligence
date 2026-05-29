import sqlite3
import sys
sys.stdout.reconfigure(encoding='utf-8')

db_path = r"C:\Users\cazam\Downloads\이력서자동분석검색시스템\candidates.db"
conn = sqlite3.connect(db_path)
cur = conn.cursor()

queries = [
    # 1. Eng_SW
    ("""
    UPDATE candidates SET sector = 'Eng_SW' WHERE name_kr IN 
    ('강희범','김주상','김대희','노진우','류길문','박유진',
     '송현민','유세진','윤석훈','윤종주','이주영','백형곤','이동혁')
    AND sector = 'Eng_Embedded'
    """, "Eng_SW 일괄 수정"),
    
    # 2. Product
    ("""
    UPDATE candidates SET sector = 'Product' WHERE name_kr IN 
    ('김관백','박준영','여성수','이겨레','이겨례','이대식')
    AND sector = 'Eng_Embedded'
    """, "Product 일괄 수정"),
    
    # 3. 김민규 (Product, Eng_SW)
    ("""
    UPDATE candidates SET sector = 'Product, Eng_SW' WHERE name_kr = '김민규'
    AND current_company LIKE '%직방%' AND sector = 'Eng_Embedded'
    """, "김민규 수정"),
    
    # 4. Eng_AI
    ("""
    UPDATE candidates SET sector = 'Eng_AI' WHERE name_kr IN 
    ('곽철현','이주성','이형덕','최현석')
    AND sector = 'Eng_Embedded'
    """, "Eng_AI 일괄 수정"),
    
    # 5. 박진배 (Eng_AI, Eng_Embedded)
    ("""
    UPDATE candidates SET sector = 'Eng_AI, Eng_Embedded' WHERE name_kr IN 
    ('박진배')
    AND sector = 'Eng_Embedded'
    """, "박진배 수정"),
    
    # 6. 이상규 (Eng_Data)
    ("""
    UPDATE candidates SET sector = 'Eng_Data' WHERE name_kr = '이상규'
    AND sector = 'Eng_Embedded'
    """, "이상규 수정"),
    
    # 7. 배성준, 이동훈 (Sales)
    ("""
    UPDATE candidates SET sector = 'Sales' WHERE name_kr IN ('배성준','이동훈')
    AND sector = 'Eng_Embedded'
    """, "배성준, 이동훈 수정"),
    
    # 8. 박현규 (Strategy)
    ("""
    UPDATE candidates SET sector = 'Strategy' WHERE name_kr = '박현규'
    AND sector = 'Eng_Embedded'
    """, "박현규 수정"),
    
    # 9. 조용석 (CIO/IT인프라 운영)
    ("""
    UPDATE candidates SET sector = 'CIO/IT인프라 운영' WHERE name_kr = '조용석'
    AND sector = 'Eng_Embedded'
    """, "조용석 CIO/IT인프라 운영 수정"),
    
    # 10. 조용석 (Operations)
    ("""
    UPDATE candidates SET sector = 'Operations' WHERE name_kr = '조용석'
    AND sector = 'Eng_Embedded'
    """, "조용석 Operations 수정")
]

print("=== Sector 일괄 수정 작업 시작 ===")
for q, desc in queries:
    cur.execute(q)
    conn.commit()
    print(f" - {desc}: {cur.rowcount}행 반영 완료")

# Eng_Embedded 남은 인원 확인
cur.execute("SELECT COUNT(*) FROM candidates WHERE sector = 'Eng_Embedded'")
remaining_count = cur.fetchone()[0]

print("\n=== 작업 완료 ===")
print(f"Eng_Embedded 남은 인원 수: {remaining_count}명")

conn.close()
