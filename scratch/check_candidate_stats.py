import sqlite3
import sys

def check_stats():
    sys.stdout.reconfigure(encoding='utf-8')
    conn = sqlite3.connect('candidates.db')
    cur = conn.cursor()

    # 1. No contact info (phone AND email)
    cur.execute('SELECT COUNT(*) FROM candidates WHERE is_duplicate=0 AND (phone IS NULL OR phone="") AND (email IS NULL OR email="")')
    no_contact = cur.fetchone()[0]

    # 2. No Google Drive URL
    cur.execute('SELECT COUNT(*) FROM candidates WHERE is_duplicate=0 AND (google_drive_url IS NULL OR google_drive_url="")')
    no_cv = cur.fetchone()[0]

    # 3. Total masters
    cur.execute('SELECT COUNT(*) FROM candidates WHERE is_duplicate=0')
    total = cur.fetchone()[0]

    print(f'전체 마스터: {total}명')
    print(f'연락처 없음: {no_contact}명 ({no_contact/total*100:.1f}%)')
    print(f'이력서 링크 없음: {no_cv}명 ({no_cv/total*100:.1f}%)')

    # 4. Search for Kim Han-soo
    print("\n--- 검색 결과: 김한수 ---")
    cur.execute('SELECT id, name_kr, phone, email, google_drive_url, is_duplicate FROM candidates WHERE name_kr LIKE "%김한수%"')
    rows = cur.fetchall()
    if not rows:
        print("검색 결과 없음")
    for r in rows:
        print(f'결과: {r}')

    conn.close()

if __name__ == "__main__":
    check_stats()
