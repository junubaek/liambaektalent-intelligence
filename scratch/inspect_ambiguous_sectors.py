import sqlite3
import sys

def main():
    sys.stdout.reconfigure(encoding='utf-8')
    conn = sqlite3.connect('candidates.db')
    cur = conn.cursor()

    # 1. First Query: Sector with Sample Names
    print("=== [1] 주요 Sector별 실제 인물 샘플 (상위 50개 섹터, 5명 이상 소속) ===")
    cur.execute("""
        SELECT 
            sector,
            COUNT(*) as cnt,
            GROUP_CONCAT(name_kr || '(' || COALESCE(current_company,'미상') || ')', ' / ') as samples
        FROM (
            SELECT sector, name_kr, current_company
            FROM candidates
            WHERE sector IS NOT NULL
            ORDER BY id  -- Replace RANDOM() with deterministic order for stable script, we will limit group concat in python
        ) sub
        GROUP BY sector
        HAVING cnt >= 5
        ORDER BY cnt DESC
        LIMIT 50
    """)
    rows = cur.fetchall()
    for i, r in enumerate(rows):
        sector = r[0]
        cnt = r[1]
        raw_samples = r[2].split(' / ')
        # Get up to 5 samples
        samples_str = " / ".join(raw_samples[:5])
        print(f"[{i+1:>2}] {sector} (총 {cnt}명):")
        print(f"    ➔ {samples_str}")
        print("-" * 80)

    # 2. Second Query: Deep Dive into Ambiguous Sectors
    print("\n\n=== [2] 애매한 주요 Sector 소속 인물 정밀 확인 ===")
    ambiguous_sectors = [
        'Operations', 'Engineering', 'IT/플랫폼', 
        'Backend', 'Infrastructure_and_Cloud',
        'Machine_Learning', 'Deep_Learning',
        'Data_Analysis', 'SW (Software)',
        'Finance (재무/회계)', 'Human Resources'
    ]
    
    placeholders = ','.join(['?'] * len(ambiguous_sectors))
    cur.execute(f"""
        SELECT sector, name_kr, current_company, total_years, profile_summary
        FROM candidates
        WHERE sector IN ({placeholders})
        ORDER BY sector, total_years DESC
    """, ambiguous_sectors)
    
    rows_amb = cur.fetchall()
    
    current_sector = None
    count = 0
    for r in rows_amb:
        sec = r[0]
        name = r[1]
        comp = r[2] or '미상'
        years = r[3] or 0.0
        summary = r[4] or '요약 없음'
        
        if sec != current_sector:
            current_sector = sec
            print(f"\n📂 [{current_sector}] Sector 상세 목록:")
            count = 0
            
        count += 1
        if count <= 6:  # Print up to 6 per sector to prevent overflow but give extremely deep view
            trimmed_sum = summary[:110] + "..." if len(summary) > 110 else summary
            print(f"  ({count}) {name} ({years}년차) | 회사: {comp}")
            print(f"      - 요약: {trimmed_sum}")
            
    conn.close()

if __name__ == '__main__':
    main()
