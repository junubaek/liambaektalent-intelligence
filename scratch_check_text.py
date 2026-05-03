import sqlite3
conn = sqlite3.connect('candidates.db')
cid = '31f22567-1b6f-81ec-aa3c-f1a606d11227'
r = conn.execute("SELECT name_kr, raw_text FROM candidates WHERE id=?", (cid,)).fetchone()
if r:
    text = r[1].upper()
    print(f"Has SCM: {'SCM' in text}")
    print(f"Has 구매: {'구매' in text}")
    print(f"Has Sourcing: {'SOURCING' in text}")
    print(f"Has Negotiation: {'NEGOTIATION' in text}")
    print(f"Has 협상: {'협상' in text}")
else:
    print("NOT FOUND")
conn.close()
