import sqlite3
import re
con = sqlite3.connect('candidates.db')
c = con.cursor()
rows = c.execute("SELECT id, raw_text FROM candidates WHERE is_duplicate=0 AND (email IS NULL OR email='')").fetchall()
emails_updated = 0
phones_updated = 0

for r in rows:
    cid = r[0]
    raw = r[1]
    if not raw: continue
    
    header_text = raw[:2000]
    
    emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', header_text)
    phones = re.findall(r'010[-\s]?\d{4}[-\s]?\d{4}', header_text)
    
    q_parts = []
    params = []
    
    if emails:
        q_parts.append("email=?")
        params.append(emails[0])
        emails_updated += 1
        
    if phones:
        q_parts.append("phone=?")
        params.append(phones[0].replace(' ', '-'))
        phones_updated += 1
        
    if q_parts:
        params.append(cid)
        c.execute(f"UPDATE candidates SET {', '.join(q_parts)} WHERE id=?", params)

con.commit()
print(f"Emails updated: {emails_updated}")
print(f"Phones updated: {phones_updated}")
