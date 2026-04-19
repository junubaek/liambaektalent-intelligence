import sqlite3

query = """
SELECT '게임기획' as type, count(*) as cnt FROM candidates WHERE raw_text LIKE '%게임 기획%' OR raw_text LIKE '%게임기획%'
UNION ALL
SELECT 'QA', count(*) FROM candidates WHERE raw_text LIKE '%QA%' OR raw_text LIKE '%품질%' OR raw_text LIKE '%테스트%'
UNION ALL
SELECT '정보보안', count(*) FROM candidates WHERE raw_text LIKE '%정보보안%' OR raw_text LIKE '%보안%'
UNION ALL
SELECT '모의해킹', count(*) FROM candidates WHERE raw_text LIKE '%모의해킹%' OR raw_text LIKE '%침투테스트%' OR raw_text LIKE '%Penetration%'
UNION ALL
SELECT 'BI분석', count(*) FROM candidates WHERE raw_text LIKE '%Tableau%' OR raw_text LIKE '%BI%' OR raw_text LIKE '%대시보드%'
UNION ALL
SELECT '커머스MD', count(*) FROM candidates WHERE raw_text LIKE '% MD%' OR raw_text LIKE '%머천다이징%' OR raw_text LIKE '%상품기획%'
UNION ALL
SELECT 'HRBP', count(*) FROM candidates WHERE raw_text LIKE '%HRBP%' OR raw_text LIKE '%HR BP%'
UNION ALL
SELECT 'L&D', count(*) FROM candidates WHERE raw_text LIKE '%L&D%' OR raw_text LIKE '%교육 담당%' OR raw_text LIKE '%HRD%'
UNION ALL
SELECT 'VC심사역', count(*) FROM candidates WHERE raw_text LIKE '%VC%' OR raw_text LIKE '%심사역%' OR raw_text LIKE '%벤처투자%'
UNION ALL
SELECT 'BizOps', count(*) FROM candidates WHERE raw_text LIKE '%Biz-Ops%' OR raw_text LIKE '%비즈옵스%' OR raw_text LIKE '%운영기획%'
UNION ALL
SELECT '파트너십', count(*) FROM candidates WHERE raw_text LIKE '%파트너십%' OR raw_text LIKE '%제휴%'
UNION ALL
SELECT '앱마케터', count(*) FROM candidates WHERE raw_text LIKE '%UA%' OR raw_text LIKE '%앱 마케팅%' OR raw_text LIKE '%앱마케팅%'
UNION ALL
SELECT '모션그래픽', count(*) FROM candidates WHERE raw_text LIKE '%모션%' OR raw_text LIKE '%애프터이펙트%'
UNION ALL
SELECT '핀테크컴플라이언스', count(*) FROM candidates WHERE raw_text LIKE '%핀테크%' AND (raw_text LIKE '%컴플라이언스%' OR raw_text LIKE '%규제%')
UNION ALL
SELECT '헬스케어PM', count(*) FROM candidates WHERE raw_text LIKE '%헬스케어%' OR raw_text LIKE '%의료%'
UNION ALL
SELECT '이커머스운영', count(*) FROM candidates WHERE raw_text LIKE '%이커머스%' OR raw_text LIKE '%e-commerce%'
"""

def main():
    conn = sqlite3.connect("candidates.db")
    cursor = conn.cursor()
    cursor.execute(query)
    rows = cursor.fetchall()
    
    print(f"{'분야 (Type)':<20} | {'모수 (Count)':<10}")
    print("-" * 35)
    for row in rows:
        print(f"{row[0]:<20} | {row[1]:<10}")
        
    conn.close()

if __name__ == "__main__":
    main()
