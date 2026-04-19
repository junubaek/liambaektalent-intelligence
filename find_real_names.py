import sqlite3

db = sqlite3.connect('candidates.db')
names = ['어울림', '한샘', '인리더', '요)_', '호_', '플랫폼', '강한']
q = f"""
SELECT id, name_kr, raw_text
FROM candidates 
WHERE name_kr IN ('어울림', '한샘', '인리더', '요)_', '호_', '플랫폼', '강한')
OR name_kr LIKE '%데이터%'
"""
res = db.execute(q).fetchall()

for r in res:
    print(f"=== {r[1]} ({r[0]}) ===")
    print(r[2][:300] if r[2] else "NO TEXT")
    print("\n")
