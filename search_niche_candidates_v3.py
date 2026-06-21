import sqlite3
import sys

def main():
    sys.stdout.reconfigure(encoding='utf-8')
    conn = sqlite3.connect('candidates.db')
    cur = conn.cursor()

    # Broad search NOC
    print("=== NOC/NoC Broad Search (Regardless of Company) ===")
    cur.execute("""
        SELECT id, name_kr, current_company, sector
        FROM candidates
        WHERE is_duplicate=0
        AND (raw_text LIKE '%noc%' OR raw_text LIKE '%network%on%chip%' OR profile_summary LIKE '%noc%')
    """)
    rows = cur.fetchall()
    for r in rows:
        print(f"  이름: {r[1]} | 회사: {r[2]} | sector: {r[3]} | ID: {r[0]}")
    if not rows:
        print("  None")

    # Broad search XCE / XCENA
    print("\n=== XCE/XCENA Broad Search (Regardless of Last Name) ===")
    cur.execute("""
        SELECT id, name_kr, current_company, sector
        FROM candidates
        WHERE is_duplicate=0
        AND (raw_text LIKE '%xce%' OR raw_text LIKE '%xcena%' OR raw_text LIKE '%엑스씨이%')
    """)
    rows = cur.fetchall()
    for r in rows:
        print(f"  이름: {r[1]} | 회사: {r[2]} | sector: {r[3]} | ID: {r[0]}")
    if not rows:
        print("  None")

    conn.close()

if __name__ == '__main__':
    main()
