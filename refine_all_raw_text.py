
import sys
import sqlite3
import re
import os

# Set output encoding to utf-8
sys.stdout.reconfigure(encoding='utf-8')

db_path = r'c:\Users\cazam\Downloads\이력서자동분석검색시스템\candidates.db'

if not os.path.exists(db_path):
    print(f"Database not found: {db_path}")
    sys.exit(1)

conn = sqlite3.connect(db_path)
cur = conn.cursor()

print("전체 후보자 raw_text 정제 프로세스 시작...")
cur.execute('SELECT id, raw_text FROM candidates WHERE raw_text IS NOT NULL')
rows = cur.fetchall()

fixed_count = 0
total_count = len(rows)

for idx, (cid, raw) in enumerate(rows):
    if not raw: continue
    
    fixed = raw
    
    # 1. Null 문자 정제
    if '\x00' in fixed:
        fixed = fixed.replace('\x00', ' ')
    
    # 2. 공백 비율 분석 및 개행 처리
    # (공백 비율 3% 미만인 경우 개행문자가 공백 역할을 하고 있을 가능성 큼)
    try:
        space_ratio = fixed.count(' ') / len(fixed) if len(fixed) > 0 else 1.0
        if space_ratio < 0.03:
            fixed = fixed.replace('\n', ' ')
    except:
        pass
    
    # 3. 특수문자 정제
    fixed = fixed.replace('\r', ' ')
    
    # 4. 연속 공백 정리 (3개 이상의 연속 공백을 2개로 축소)
    fixed = re.sub(r' {3,}', '  ', fixed)
    
    if fixed != raw:
        cur.execute('UPDATE candidates SET raw_text=? WHERE id=?', (fixed, cid))
        fixed_count += 1
    
    if idx % 1000 == 0 and idx > 0:
        print(f"  진행 중... {idx}/{total_count}")

conn.commit()
conn.close()

print(f"\n작업 완료: 총 {total_count}명 중 {fixed_count}명의 텍스트가 정제되었습니다.")
