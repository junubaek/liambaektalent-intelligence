import sqlite3

def run_checks():
    conn = sqlite3.connect('candidates.db')
    cursor = conn.cursor()
    
    print("=== 1. SQLite 정확한 확인 ===")
    query1 = """
    SELECT 
      COUNT(*) as total,
      SUM(CASE WHEN name_kr = '김대용' THEN 1 ELSE 0 END) as exact_match,
      SUM(CASE WHEN name_kr LIKE '%김대용%' THEN 1 ELSE 0 END) as includes_match,
      SUM(CASE WHEN name_kr IS NULL OR name_kr = '' THEN 1 ELSE 0 END) as no_name
    FROM candidates
    """
    cursor.execute(query1)
    res1 = cursor.fetchone()
    print(f"전체: {res1[0]}")
    print(f"김대용_정확히: {res1[1]}")
    print(f"김대용_포함: {res1[2]}")
    print(f"이름없음: {res1[3]}")
    
    print("\n=== 2. 이름 분포 확인 ===")
    query2 = """
    SELECT name_kr, count(*) as cnt
    FROM candidates
    GROUP BY name_kr
    ORDER BY cnt DESC
    LIMIT 20
    """
    cursor.execute(query2)
    res2 = cursor.fetchall()
    for row in res2:
        print(f"{row[0]}: {row[1]}")
        
    conn.close()

if __name__ == '__main__':
    run_checks()
