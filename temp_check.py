import sqlite3
import re
con = sqlite3.connect('candidates.db')
c = con.cursor()
rows = c.execute("SELECT id, raw_text FROM candidates WHERE is_duplicate=0 AND (email IS NULL OR email='')").fetchall()
found_emails = 0
found_phones = 0
for r in rows:
    raw = r[1]
    if not raw: continue
    
    # 1000자 이내에서 찾기 (연락처는 상단에 위치)
    header_text = raw[:2000]
    
    emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', header_text)
    if emails:
        found_emails += 1
        
    phones = re.findall(r'010[-\s]?\d{4}[-\s]?\d{4}', header_text)
    if phones:
        found_phones += 1
        
print(f"Total missing email/phone: {len(rows)}")
print(f"Regex found emails: {found_emails}")
print(f"Regex found phones: {found_phones}")
