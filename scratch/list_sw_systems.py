import sqlite3
import sys

def main():
    sys.stdout.reconfigure(encoding='utf-8')
    conn = sqlite3.connect('candidates.db')
    cur = conn.cursor()

    cur.execute("""
        SELECT id, name_kr, current_company, total_years, profile_summary 
        FROM candidates 
        WHERE sector = 'SW_Systems'
        ORDER BY total_years DESC
    """)
    rows = cur.fetchall()
    
    print(f"=== SW_Systems Sector 후보자 리스트 (총 {len(rows)}명) ===")
    for i, r in enumerate(rows):
        cid = r[0]
        name = r[1]
        company = r[2] or '미상'
        years = r[3] or 0.0
        summary = r[4] or '요약 없음'
        # Trim summary to fit nicely
        trimmed_summary = summary[:120] + "..." if len(summary) > 120 else summary
        print(f"[{i+1}] {name} ({years}년차) | 회사: {company}")
        print(f"    - ID: {cid}")
        print(f"    - 요약: {trimmed_summary}")
        print("-" * 80)

    conn.close()

if __name__ == '__main__':
    main()
