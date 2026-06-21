import sqlite3, sys, os
sys.stdout.reconfigure(encoding='utf-8')
conn = sqlite3.connect(os.path.join(os.path.dirname(__file__), '..', 'candidates.db'))
cur = conn.cursor()

# 배유정 sector Finance → Marketing
cur.execute("UPDATE candidates SET sector='Marketing' WHERE name_kr='배유정' AND is_duplicate=0")
print('배유정:', cur.rowcount)

# 강건규 경력0 레코드 중복처리
cur.execute("""
    UPDATE candidates SET is_duplicate=1
    WHERE name_kr='강건규'
    AND (email IS NULL OR email='')
    AND (total_years=0 OR total_years IS NULL)
    AND is_duplicate=0
""")
print('강건규 중복처리:', cur.rowcount)

# 배문성 sector Operations
cur.execute("UPDATE candidates SET sector='Operations' WHERE name_kr='배문성' AND is_duplicate=0")
print('배문성:', cur.rowcount)

# 최우성 Rebellions sector Sales
cur.execute("""
    UPDATE candidates SET sector='Sales'
    WHERE name_kr='최우성'
    AND current_company LIKE '%Rebellions%'
    AND is_duplicate=0
""")
print('최우성(Rebellions):', cur.rowcount)

conn.commit()
conn.close()
print('재적용 완료')
