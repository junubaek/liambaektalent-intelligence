import sqlite3

sql = """
SELECT '증권애널리스트' as type, count(*) as cnt FROM candidates WHERE raw_text LIKE '%애널리스트%' OR raw_text LIKE '%리서치%' AND raw_text LIKE '%증권%'
UNION ALL
SELECT '신용분석', count(*) FROM candidates WHERE raw_text LIKE '%신용분석%' OR raw_text LIKE '%여신%' OR raw_text LIKE '%신용평가%'
UNION ALL
SELECT '보험계리', count(*) FROM candidates WHERE raw_text LIKE '%계리%' OR raw_text LIKE '%보험수리%'
UNION ALL
SELECT '외환딜러', count(*) FROM candidates WHERE raw_text LIKE '%외환%' AND raw_text LIKE '%딜러%' OR raw_text LIKE '%FX Trading%'
UNION ALL
SELECT '금융규제', count(*) FROM candidates WHERE raw_text LIKE '%금융규제%' OR raw_text LIKE '%금감원%' OR raw_text LIKE '%금융당국%'
UNION ALL
SELECT 'RA인허가', count(*) FROM candidates WHERE raw_text LIKE '%인허가%' OR raw_text LIKE '%RA%' AND raw_text LIKE '%허가%'
UNION ALL
SELECT '신약개발', count(*) FROM candidates WHERE raw_text LIKE '%신약%' OR raw_text LIKE '%drug discovery%'
UNION ALL
SELECT '의료기기', count(*) FROM candidates WHERE raw_text LIKE '%의료기기%' OR raw_text LIKE '%medical device%'
UNION ALL
SELECT '영상PD', count(*) FROM candidates WHERE raw_text LIKE '%연출%' OR raw_text LIKE '% PD %' OR raw_text LIKE '%영상 제작%'
UNION ALL
SELECT '시나리오작가', count(*) FROM candidates WHERE raw_text LIKE '%시나리오%' OR raw_text LIKE '%스크립트%' OR raw_text LIKE '%각본%'
UNION ALL
SELECT '유튜브', count(*) FROM candidates WHERE raw_text LIKE '%유튜브%' OR raw_text LIKE '%YouTube%'
UNION ALL
SELECT '웹툰', count(*) FROM candidates WHERE raw_text LIKE '%웹툰%' OR raw_text LIKE '%만화%'
UNION ALL
SELECT '패션MD', count(*) FROM candidates WHERE raw_text LIKE '%패션%' AND raw_text LIKE '%MD%'
UNION ALL
SELECT '뷰티MD', count(*) FROM candidates WHERE raw_text LIKE '%뷰티%' AND raw_text LIKE '%MD%'
UNION ALL
SELECT '식품MD', count(*) FROM candidates WHERE raw_text LIKE '%식품%' AND raw_text LIKE '%MD%'
UNION ALL
SELECT '구매바이어', count(*) FROM candidates WHERE raw_text LIKE '%구매%' OR raw_text LIKE '%바이어%' OR raw_text LIKE '%소싱%'
UNION ALL
SELECT '건축설계', count(*) FROM candidates WHERE raw_text LIKE '%건축%' OR raw_text LIKE '%설계사%'
UNION ALL
SELECT '인테리어', count(*) FROM candidates WHERE raw_text LIKE '%인테리어%' OR raw_text LIKE '%interior%'
UNION ALL
SELECT '교육콘텐츠', count(*) FROM candidates WHERE raw_text LIKE '%교육 콘텐츠%' OR raw_text LIKE '%교육 개발%' OR raw_text LIKE '%커리큘럼%'
UNION ALL
SELECT '글로벌HR', count(*) FROM candidates WHERE raw_text LIKE '%글로벌 HR%' OR raw_text LIKE '%Global HR%' OR raw_text LIKE '%해외 인사%'
UNION ALL
SELECT '특허담당', count(*) FROM candidates WHERE raw_text LIKE '%특허%' AND (raw_text LIKE '%담당%' OR raw_text LIKE '%출원%' OR raw_text LIKE '%변리%')
"""

conn = sqlite3.connect('candidates.db')
cursor = conn.cursor()
cursor.execute(sql)
rows = cursor.fetchall()
conn.close()

with open("sqlite_counts_round4.md", "w", encoding="utf-8") as f:
    f.write("| Type | Count |\n|:---|---:|\n")
    for row in rows:
        f.write(f"| {row[0]} | {row[1]} |\n")
        
print("Done")
