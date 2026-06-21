import sqlite3
import sys

def main():
    sys.stdout.reconfigure(encoding='utf-8')
    conn = sqlite3.connect('candidates.db')
    cur = conn.cursor()

    # 1. NoC (Network on Chip) search
    print("=== [1] NoC 관련 후보자 ===")
    cur.execute("""
        SELECT id, name_kr, current_company, sector, profile_summary
        FROM candidates
        WHERE is_duplicate=0
        AND (raw_text LIKE '%noc%' OR raw_text LIKE '%network%on%chip%' OR profile_summary LIKE '%noc%')
    """)
    rows1 = cur.fetchall()
    for r in rows1:
        print(f"이름: {r[1]} | 회사: {r[2]} | sector: {r[3]} | ID: {r[0]}")
        print(f"  summary: {r[4]}")
    if not rows1:
        print("  No records found")

    # 2. XCE / XCENA & 박씨 성
    print("\n=== [2] XCE/XCENA & 박씨 성 후보자 ===")
    cur.execute("""
        SELECT id, name_kr, current_company, sector, profile_summary
        FROM candidates
        WHERE is_duplicate=0
        AND name_kr LIKE '박%'
        AND (raw_text LIKE '%xce%' OR raw_text LIKE '%xcena%' OR raw_text LIKE '%엑스씨이%')
    """)
    rows2 = cur.fetchall()
    for r in rows2:
        print(f"이름: {r[1]} | 회사: {r[2]} | sector: {r[3]} | ID: {r[0]}")
        print(f"  summary: {r[4]}")
    if not rows2:
        print("  No records found")

    conn.close()

if __name__ == '__main__':
    main()
