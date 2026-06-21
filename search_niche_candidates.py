import sqlite3
import sys

def main():
    sys.stdout.reconfigure(encoding='utf-8')
    conn = sqlite3.connect('candidates.db')
    cur = conn.cursor()

    # 1. Intel & NOC
    print("=== [1] Intel & NOC 검출 결과 ===")
    cur.execute("""
        SELECT id, name_kr, current_company, sector, profile_summary, raw_text
        FROM candidates
        WHERE is_duplicate=0
        AND (current_company LIKE '%Intel%' OR raw_text LIKE '%Intel%' OR profile_summary LIKE '%Intel%')
        AND (raw_text LIKE '%NOC%' OR raw_text LIKE '%Network%on%Chip%' OR profile_summary LIKE '%NOC%')
    """)
    rows1 = cur.fetchall()
    if rows1:
        for r in rows1:
            print(f"이름: {r[1]} | 회사: {r[2]} | sector: {r[3]} | ID: {r[0]}")
            print(f"summary: {r[4]}")
            # Find snippet of NOC
            raw = r[5] or ""
            idx = raw.lower().find("noc")
            if idx != -1:
                print(f"raw_text snippet: ...{raw[max(0, idx-50):min(len(raw), idx+100)]}...")
            print()
    else:
        print("검색 결과 없음\n")

    # 2. XCENA & 박씨 성
    print("=== [2] XCENA & 박씨 성 검출 결과 ===")
    cur.execute("""
        SELECT id, name_kr, current_company, sector, profile_summary, raw_text
        FROM candidates
        WHERE is_duplicate=0
        AND (name_kr LIKE '박%')
        AND (current_company LIKE '%XCENA%' OR raw_text LIKE '%XCENA%' OR current_company LIKE '%XCE%' OR raw_text LIKE '%XCE%')
    """)
    rows2 = cur.fetchall()
    if rows2:
        for r in rows2:
            print(f"이름: {r[1]} | 회사: {r[2]} | sector: {r[3]} | ID: {r[0]}")
            print(f"summary: {r[4]}")
            # Find snippet of XCE
            raw = r[5] or ""
            idx = raw.lower().find("xce")
            if idx != -1:
                print(f"raw_text snippet: ...{raw[max(0, idx-50):min(len(raw), idx+100)]}...")
            print()
    else:
        print("검색 결과 없음\n")

    # 3. Furiosa & Compiler
    print("=== [3] Furiosa & Compiler 검출 결과 ===")
    cur.execute("""
        SELECT id, name_kr, current_company, sector, profile_summary, raw_text
        FROM candidates
        WHERE is_duplicate=0
        AND (current_company LIKE '%Furiosa%' OR raw_text LIKE '%Furiosa%' OR profile_summary LIKE '%Furiosa%')
        AND (raw_text LIKE '%compiler%' OR profile_summary LIKE '%compiler%' OR raw_text LIKE '%컴파일러%' OR profile_summary LIKE '%컴파일러%')
    """)
    rows3 = cur.fetchall()
    if rows3:
        for r in rows3:
            print(f"이름: {r[1]} | 회사: {r[2]} | sector: {r[3]} | ID: {r[0]}")
            print(f"summary: {r[4]}")
            raw = r[5] or ""
            idx = raw.lower().find("compiler")
            if idx != -1:
                print(f"raw_text snippet: ...{raw[max(0, idx-50):min(len(raw), idx+100)]}...")
            print()
    else:
        print("검색 결과 없음\n")

    conn.close()

if __name__ == '__main__':
    main()
