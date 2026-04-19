import sqlite3
import json

print('--- 1 & 2. 백필 완료 통계 ---')
conn = sqlite3.connect(r'C:\Users\cazam\Downloads\이력서자동분석검색시스템\candidates.db')
c = conn.cursor()
c.execute('SELECT COUNT(*) FROM candidates WHERE birth_year IS NOT NULL')
by_count = c.fetchone()[0]
c.execute("SELECT COUNT(*) FROM candidates WHERE education_json IS NOT NULL AND education_json != '[]'")
edu_count = c.fetchone()[0]
print(f'birth_year 보유: {by_count}명')
print(f'education_json 보유: {edu_count}명')

print('\n--- 3. 고아 파일 분석 ---')
with open(r'C:\Users\cazam\Downloads\이력서자동분석검색시스템\missing_files_report.json', 'r', encoding='utf-8') as f:
    report = json.load(f)

unmatched = report.get('unmatched_list', [])

c.execute("SELECT phone FROM candidates WHERE phone IS NOT NULL AND phone != ''")
db_phones = set([row[0].replace('-', '').replace(' ', '') for row in c.fetchall()])

new_resumes = 0
duplicate_by_phone = 0
no_phone = 0

for u in unmatched:
    phone = u.get('extracted_phone')
    if not phone:
        no_phone += 1
    elif phone in db_phones:
        duplicate_by_phone += 1
    else:
        new_resumes += 1

print(f'총 고아 파일 검사: {len(unmatched)}건')
print(f'-> DB 전화번호 매칭 성공 (이름/파일명 달랐던 중복 파일): {duplicate_by_phone}건')
print(f'-> DB에 완전히 없는 완전체 리얼 신규 이력서 (미등록): {new_resumes}건')
print(f'-> 파일 내 연락처 추출 실패로 판독 보류: {no_phone}건')
