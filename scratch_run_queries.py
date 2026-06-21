import sqlite3
import sys

# Ensure UTF-8 output
sys.stdout.reconfigure(encoding='utf-8')

db_path = r"C:\Users\cazam\Downloads\이력서자동분석검색시스템\candidates.db"
output_path = r"C:\Users\cazam\Downloads\이력서자동분석검색시스템\query_results.md"

conn = sqlite3.connect(db_path)
cur = conn.cursor()

with open(output_path, "w", encoding="utf-8") as f:
    f.write("# SQLite Query Execution Results\n\n")
    
    # ----------------- [1] Sector별 샘플 -----------------
    f.write("## [1] Sector별 샘플 (전체 개수 & 무작위 3~5명 확인)\n\n")
    f.write("| Sector | Total Count | Sample Candidates (Name and Current Company) |\n")
    f.write("| :--- | :---: | :--- |\n")
    
    cur.execute("""
        SELECT sector, COUNT(*) as cnt
        FROM candidates
        WHERE sector IS NOT NULL
        GROUP BY sector
        HAVING cnt >= 5
        ORDER BY cnt DESC
        LIMIT 50
    """)
    sectors_info = cur.fetchall()

    for sector, cnt in sectors_info:
        cur.execute("""
            SELECT name_kr, current_company
            FROM candidates
            WHERE sector = ?
            ORDER BY RANDOM()
            LIMIT 5
        """, (sector,))
        samples_list = cur.fetchall()
        samples_str = " / ".join([f"{name}({comp if comp else '미상'})" for name, comp in samples_list])
        f.write(f"| {sector} | {cnt} | {samples_str} |\n")
        
    f.write("\n\n")
    
    # ----------------- [2] 애매한 Sector별 후보자 목록 -----------------
    f.write("## [2] 애매한 Sector별 후보자 상세 목록 (total_years 내림차순)\n\n")
    
    target_sectors = (
        'Operations', 'Engineering', 'IT/플랫폼', 
        'Backend', 'Infrastructure_and_Cloud',
        'Machine_Learning', 'Deep_Learning',
        'Data_Analysis', 'SW (Software)',
        'Finance (재무/회계)', 'Human Resources'
    )
    
    cur.execute("""
        SELECT sector, name_kr, current_company, total_years, profile_summary
        FROM candidates
        WHERE sector IN (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ORDER BY sector, total_years DESC
    """, target_sectors)
    
    rows = cur.fetchall()
    f.write(f"**총 조회된 애매한 Sector 후보자 수:** {len(rows)}명\n\n")
    
    current_sec = None
    for sector, name, company, years, summary in rows:
        if sector != current_sec:
            current_sec = sector
            f.write(f"\n### Sector: {current_sec}\n\n")
            f.write("| 이름 | 현재 회사 | 경력 (년) | 프로필 요약 |\n")
            f.write("| :--- | :--- | :---: | :--- |\n")
        
        summary_clean = (summary or "").replace('\n', ' ').strip()
        years_str = f"{years:.1f}" if years is not None else "미상"
        f.write(f"| {name} | {company if company else '미상'} | {years_str} | {summary_clean} |\n")

print("Successfully written query results to query_results.md")
conn.close()
