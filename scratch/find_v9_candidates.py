import sqlite3, json

conn = sqlite3.connect('candidates.db')
cur = conn.cursor()

# 카카오 출신 백엔드
cur.execute("""
    SELECT id, name_kr, current_company, sector, profile_summary
    FROM candidates
    WHERE is_duplicate=0
    AND sector IN ('Eng_SW', 'Eng_Data')
    AND (
        raw_text LIKE '%카카오%'
        OR raw_text LIKE '%Kakao%'
        OR current_company LIKE '%카카오%'
    )
    ORDER BY total_years DESC
    LIMIT 10
""")
print('=== 카카오 출신 백엔드 ===')
for r in cur.fetchall():
    print(f'  {r[1]} ({r[0]}) | {r[2]} | {r[3]} | {r[4][:50] if r[4] else ""}')

# 토스 출신 ML
cur.execute("""
    SELECT id, name_kr, current_company, sector, profile_summary
    FROM candidates
    WHERE is_duplicate=0
    AND sector IN ('Eng_AI', 'Eng_Data', 'Eng_SW')
    AND (
        raw_text LIKE '%토스%'
        OR raw_text LIKE '%Toss%'
        OR raw_text LIKE '%비바리퍼블리카%'
    )
    ORDER BY total_years DESC
    LIMIT 10
""")
print('\n=== 토스 출신 ML/개발자 ===')
for r in cur.fetchall():
    print(f'  {r[1]} ({r[0]}) | {r[2]} | {r[3]} | {r[4][:50] if r[4] else ""}')

# 리벨리온/퓨리오사 NPU
cur.execute("""
    SELECT id, name_kr, current_company, sector, profile_summary
    FROM candidates
    WHERE is_duplicate=0
    AND (
        raw_text LIKE '%리벨리온%'
        OR raw_text LIKE '%Rebellions%'
        OR raw_text LIKE '%퓨리오사%'
        OR raw_text LIKE '%FuriosaAI%'
    )
    LIMIT 10
""")
print('\n=== 리벨리온/퓨리오사 NPU ===')
for r in cur.fetchall():
    print(f'  {r[1]} ({r[0]}) | {r[2]} | {r[3]} | {r[4][:50] if r[4] else ""}')

# 스타트업 CTO 경험
cur.execute("""
    SELECT id, name_kr, current_company, sector, profile_summary
    FROM candidates
    WHERE is_duplicate=0
    AND sector IN ('Eng_SW', 'Eng_AI', 'Product', 'Strategy')
    AND (
        raw_text LIKE '%CTO%'
        OR raw_text LIKE '%기술총괄%'
        OR raw_text LIKE '%최고기술%'
    )
    ORDER BY total_years DESC
    LIMIT 10
""")
print('\n=== 스타트업 CTO 경험 ===')
for r in cur.fetchall():
    print(f'  {r[1]} ({r[0]}) | {r[2]} | {r[3]} | {r[4][:50] if r[4] else ""}')

# IPO 경험 CFO
cur.execute("""
    SELECT id, name_kr, current_company, sector, profile_summary
    FROM candidates
    WHERE is_duplicate=0
    AND sector = 'Finance'
    AND (
        raw_text LIKE '%IPO%'
        OR raw_text LIKE '%기업공개%'
        OR raw_text LIKE '%상장%'
    )
    ORDER BY total_years DESC
    LIMIT 10
""")
print('\n=== IPO 경험 CFO/재무 ===')
for r in cur.fetchall():
    print(f'  {r[1]} ({r[0]}) | {r[2]} | {r[3]} | {r[4][:50] if r[4] else ""}')

# 네이버 출신 검색/개발
cur.execute("""
    SELECT id, name_kr, current_company, sector, profile_summary
    FROM candidates
    WHERE is_duplicate=0
    AND sector IN ('Eng_SW', 'Eng_AI', 'Eng_Data')
    AND (
        raw_text LIKE '%네이버%'
        OR raw_text LIKE '%NAVER%'
        OR current_company LIKE '%네이버%'
    )
    ORDER BY total_years DESC
    LIMIT 10
""")
print('\n=== 네이버 출신 개발자 ===')
for r in cur.fetchall():
    print(f'  {r[1]} ({r[0]}) | {r[2]} | {r[3]} | {r[4][:50] if r[4] else ""}')

conn.close()
