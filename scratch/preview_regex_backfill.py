import sqlite3
import re
import sys

def preview_regex_extraction():
    sys.stdout.reconfigure(encoding='utf-8')
    conn = sqlite3.connect('candidates.db')
    cur = conn.cursor()

    # 1. Check masters with missing current_company
    cur.execute('''SELECT COUNT(*) FROM candidates 
                   WHERE is_duplicate=0 
                   AND (current_company IS NULL OR current_company="")
                   AND raw_text IS NOT NULL AND length(raw_text) > 100''')
    missing_company_cnt = cur.fetchone()[0]
    print(f'current_company 비어있는 후보자: {missing_company_cnt}명')

    # 2. Preview Phone/Email extraction for masters with missing contact info
    cur.execute('''SELECT id, name_kr, raw_text FROM candidates
                   WHERE is_duplicate=0
                   AND ((phone IS NULL OR phone="") OR (email IS NULL OR email=""))
                   AND raw_text IS NOT NULL AND length(raw_text) > 100
                   LIMIT 10''')
    samples = cur.fetchall()
    
    print('\n--- 샘플 raw_text 정규식 추출 결과 (Top 10) ---')
    phone_pattern = re.compile(r'01[0-9][-\s]?\d{3,4}[-\s]?\d{4}|\+82[-\s]?10[-\s]?\d{3,4}[-\s]?\d{4}')
    email_pattern = re.compile(r'[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}')
    
    # Simple company pattern: look for lines starting with some common patterns or before "Present"
    # This is a very naive company extractor for preview
    company_pattern = re.compile(r'([^\n]+)\s+\|?\s+(?:Present|현재|20[12]\d년?\s*\d?월?\s*-\s*Present)', re.IGNORECASE)

    for cid, name, raw in samples:
        phones = phone_pattern.findall(raw or '')
        emails = email_pattern.findall(raw or '')
        
        # Try to find potential current company
        potential_companies = company_pattern.findall(raw or '')
        
        print(f'후보자: {name} ({cid})')
        print(f'  [추출] Phone: {phones[:1]}')
        print(f'  [추출] Email: {emails[:1]}')
        if potential_companies:
            print(f'  [추출] Potential Company: {potential_companies[0].strip()[:50]}')
        print("-" * 30)

    conn.close()

if __name__ == "__main__":
    preview_regex_extraction()
