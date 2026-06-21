import sqlite3

conn = sqlite3.connect('candidates.db')
cur = conn.cursor()

cur.execute("""
    SELECT id, name_kr, current_company, sector, profile_summary
    FROM candidates
    WHERE is_duplicate = 0
    AND (
        raw_text LIKE '%삼성%'
        OR raw_text LIKE '%Samsung%'
    )
    AND (
        raw_text LIKE '%SoC%'
        OR raw_text LIKE '%설계%'
        OR raw_text LIKE '%ASIC%'
        OR raw_text LIKE '%RTL%'
    )
    LIMIT 20
""")

print("Potential real Samsung SoC Engineers:")
for r in cur.fetchall():
    print(f"  ID: {r[0]} | Name: {r[1]} | Company: {r[2]} | Sector: {r[3]} | Summary: {r[4][:100] if r[4] else ''}")

conn.close()
