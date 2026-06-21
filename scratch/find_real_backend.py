import sqlite3

conn = sqlite3.connect('candidates.db')
cur = conn.cursor()

# Find candidates who have Kakao/카카오 AND backend keywords in their resume
cur.execute("""
    SELECT id, name_kr, current_company, sector, profile_summary
    FROM candidates
    WHERE is_duplicate = 0
    AND (
        raw_text LIKE '%카카오%'
        OR raw_text LIKE '%Kakao%'
    )
    AND (
        raw_text LIKE '%백엔드%'
        OR raw_text LIKE '%Backend%'
        OR raw_text LIKE '%Java%'
        OR raw_text LIKE '%Spring%'
    )
    LIMIT 20
""")

print("Potential real Kakao Backend Developers:")
for r in cur.fetchall():
    print(f"  ID: {r[0]} | Name: {r[1]} | Company: {r[2]} | Sector: {r[3]} | Summary: {r[4][:100] if r[4] else ''}")

conn.close()
