import sqlite3
import sys

def deep_check():
    sys.stdout.reconfigure(encoding='utf-8')
    conn = sqlite3.connect('candidates.db')
    cur = conn.cursor()

    # 1. Detailed check for Kim Han-soo
    print("--- 김한수 상세 정보 ---")
    cur.execute('''SELECT id, name_kr, current_company, phone, email, 
                   google_drive_url, profile_summary, raw_text
                   FROM candidates WHERE name_kr LIKE "%김한수%" AND is_duplicate=0''')
    row = cur.fetchone()
    if row:
        print(f'ID: {row[0]}')
        print(f'이름: {row[1]}')
        print(f'현재 회사: {row[2]}')
        print(f'전화번호: {row[3]}')
        print(f'이메일: {row[4]}')
        print(f'드라이브 URL: {row[5]}')
        print(f'프로필 요약: {row[6]}')
        print(f'이력서 원문 (앞 300자):')
        if row[7]:
            print(row[7][:300])
        else:
            print("원문 없음")
    else:
        print("김한수(마스터)를 찾을 수 없습니다.")

    # 2. Check raw_text for 601 candidates without contact info
    cur.execute('''SELECT COUNT(*) FROM candidates 
                   WHERE is_duplicate=0 
                   AND (phone IS NULL OR phone="") 
                   AND (email IS NULL OR email="")
                   AND raw_text IS NOT NULL AND length(raw_text) > 100''')
    has_raw = cur.fetchone()[0]
    print(f'\n--- 연락처 미보유자 분석 ---')
    print(f'연락처가 없지만 유의미한 raw_text(100자 이상)가 있는 후보자: {has_raw}명')

    conn.close()

if __name__ == "__main__":
    deep_check()
