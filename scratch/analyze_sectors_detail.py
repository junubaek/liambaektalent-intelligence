import sqlite3
import sys

def main():
    sys.stdout.reconfigure(encoding='utf-8')
    conn = sqlite3.connect('candidates.db')
    cur = conn.cursor()

    # 1. Product Owner sector check
    cur.execute("""
        SELECT sector, COUNT(*) 
        FROM candidates 
        WHERE profile_summary LIKE '%Product Owner%' 
           OR profile_summary LIKE '%PO%' 
           OR raw_text LIKE '%Product Owner%'
        GROUP BY sector
        ORDER BY COUNT(*) DESC
        LIMIT 15
    """)
    print('=== Product Owner (PO) Candidates Sector Distribution ===')
    for r in cur.fetchall():
        print(f'  - {r[0]}: {r[1]}명')

    # 2. SCM sector check
    print('\n=== SCM Candidates Sector Distribution ===')
    cur.execute("""
        SELECT sector, COUNT(*) 
        FROM candidates 
        WHERE profile_summary LIKE '%SCM%' 
           OR raw_text LIKE '%SCM%' 
           OR raw_text LIKE '%공급망%'
        GROUP BY sector
        ORDER BY COUNT(*) DESC
        LIMIT 15
    """)
    for r in cur.fetchall():
        print(f'  - {r[0]}: {r[1]}명')

    # 3. Product sector existence check
    print('\n=== Sector column including "Product" ===')
    cur.execute("""
        SELECT sector, COUNT(*) 
        FROM candidates 
        WHERE sector LIKE '%Product%'
        GROUP BY sector
        ORDER BY COUNT(*) DESC
    """)
    for r in cur.fetchall():
        print(f'  - {r[0]}: {r[1]}명')

    # 4. Total and others count
    cur.execute("SELECT COUNT(*) FROM candidates")
    total = cur.fetchone()[0]
    
    cur.execute("""
        SELECT COUNT(*) FROM candidates 
        WHERE sector IN ('SW', 'Semiconductor_SoC', 'Semiconductor_NPU', 'SW_AI', 'SW_Systems', 'Semiconductor')
    """)
    core_tech_count = cur.fetchone()[0]
    
    print(f'\n=== 전체 대비 기타 섹터 요약 ===')
    print(f'  - 전체 후보자 수: {total}명')
    print(f'  - 핵심 IT/반도체 섹터 인원 (SW/AI/Systems/SoC/NPU/Semicon): {core_tech_count}명')
    print(f'  - 그 외 비즈니스/마케팅/운영/기타 섹터 인원: {total - core_tech_count}명')

    conn.close()

if __name__ == '__main__':
    main()
