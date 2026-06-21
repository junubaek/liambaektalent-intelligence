import sqlite3
import sys

def main():
    sys.stdout.reconfigure(encoding='utf-8')
    conn = sqlite3.connect('candidates.db')
    cur = conn.cursor()

    # 1. NOC & Intel
    print("=== [1] Intel & NOC ===")
    cur.execute("""
        SELECT id, name_kr, current_company, sector, profile_summary
        FROM candidates
        WHERE is_duplicate=0
        AND (raw_text LIKE '%noc%' OR raw_text LIKE '%network%on%chip%' OR profile_summary LIKE '%noc%')
        AND (raw_text LIKE '%intel%' OR current_company LIKE '%intel%' OR profile_summary LIKE '%intel%')
    """)
    for r in cur.fetchall():
        print(f"  이름: {r[1]} | 회사: {r[2]} | sector: {r[3]} | ID: {r[0]}")
        print(f"  summary: {r[4]}")

    # 2. XCE & Park (name starts with 박)
    print("\n=== [2] XCE/XCENA & 박씨 ===")
    cur.execute("""
        SELECT id, name_kr, current_company, sector, profile_summary
        FROM candidates
        WHERE is_duplicate=0
        AND name_kr LIKE '박%'
        AND (raw_text LIKE '%xce%' OR raw_text LIKE '%xcena%' OR raw_text LIKE '%엑스씨이%')
    """)
    for r in cur.fetchall():
        print(f"  이름: {r[1]} | 회사: {r[2]} | sector: {r[3]} | ID: {r[0]}")
        print(f"  summary: {r[4]}")

    # 3. Furiosa & Compiler
    print("\n=== [3] Furiosa & Compiler ===")
    cur.execute("""
        SELECT id, name_kr, current_company, sector, profile_summary
        FROM candidates
        WHERE is_duplicate=0
        AND (raw_text LIKE '%furiosa%' OR current_company LIKE '%furiosa%' OR profile_summary LIKE '%furiosa%')
        AND (raw_text LIKE '%compiler%' OR raw_text LIKE '%컴파일러%' OR profile_summary LIKE '%compiler%' OR profile_summary LIKE '%컴파일러%')
    """)
    for r in cur.fetchall():
        print(f"  이름: {r[1]} | 회사: {r[2]} | sector: {r[3]} | ID: {r[0]}")
        print(f"  summary: {r[4]}")

    conn.close()

if __name__ == '__main__':
    main()
