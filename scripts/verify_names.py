import sqlite3

def verify_names():
    conn = sqlite3.connect('candidates.db')
    c = conn.cursor()
    c.execute("SELECT name_kr, count(*) FROM candidates WHERE is_duplicate=0 AND name_kr IN ('임정훈', '왕자현', '최예리') GROUP BY name_kr")
    results = c.fetchall()
    
    print("\n========= VALIDATION RESULTS =========")
    for row in results:
        print(f"Name: {row[0]} -> Output Count: {row[1]}")
    
    c.execute("SELECT name_kr, count(*) as cnt FROM candidates WHERE is_duplicate=0 GROUP BY name_kr HAVING cnt > 1")
    dupes = c.fetchall()
    print(f"\nTotal duplicate names globally remaining: {len(dupes)}")

if __name__ == "__main__":
    verify_names()
