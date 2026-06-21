import sqlite3

conn = sqlite3.connect('candidates.db')
cur = conn.cursor()

# Tier Distribution
cur.execute("""
    SELECT json_extract(cei_json, '$.company_signal.tier') as tier,
           COUNT(*) as cnt
    FROM candidates
    WHERE cei_json IS NOT NULL AND is_duplicate=0
    GROUP BY tier ORDER BY cnt DESC
""")
print("Tier 분포:")
for r in cur.fetchall():
    print(f"  {r[0]}: {r[1]}명")

# Inference Flag
cur.execute("""
    SELECT json_extract(cei_json, '$.inference_flag') as flag,
           COUNT(*) as cnt
    FROM candidates
    WHERE cei_json IS NOT NULL AND is_duplicate=0
    GROUP BY flag
""")
print("\n추론 플래그 분포 (inference_flag):")
for r in cur.fetchall():
    print(f"  {r[0]}: {r[1]}명")

conn.close()
