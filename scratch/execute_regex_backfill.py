import sqlite3
import re
import sys

def backfill_missing_metadata():
    sys.stdout.reconfigure(encoding='utf-8')
    conn = sqlite3.connect('candidates.db')
    cur = conn.cursor()

    # Patterns
    phone_pattern = re.compile(r'01[0-9][-\s]?\d{3,4}[-\s]?\d{4}|\+82[-\s]?10[-\s]?\d{3,4}[-\s]?\d{4}')
    email_pattern = re.compile(r'[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}')
    # Naive company pattern: Look for lines that likely contain a company name near keywords like Present/현재
    company_keywords = ['Present', '현재', '재직 중', '재직중', '방금', '지금']
    
    # Get all masters with missing data
    cur.execute('''SELECT id, name_kr, raw_text, phone, email, current_company 
                   FROM candidates 
                   WHERE is_duplicate=0 
                   AND (
                       (phone IS NULL OR phone="") OR 
                       (email IS NULL OR email="") OR 
                       (current_company IS NULL OR current_company="")
                   )
                   AND raw_text IS NOT NULL AND length(raw_text) > 50''')
    rows = cur.fetchall()
    
    print(f'처리 대상 후보자: {len(rows)}명')
    
    updated_count = 0
    for cid, name, raw, existing_phone, existing_email, existing_company in rows:
        updates = {}
        
        # 1. Phone
        if not existing_phone:
            phones = phone_pattern.findall(raw)
            if phones:
                updates['phone'] = phones[0].strip()
        
        # 2. Email
        if not existing_email:
            emails = email_pattern.findall(raw)
            if emails:
                updates['email'] = emails[0].strip()
        
        # 3. Current Company (Improved heuristic)
        if not existing_company:
            # Heuristic: Find first line after "경력" or "Experience" or lines with company keywords
            lines = raw.split('\n')
            found_company = None
            for i, line in enumerate(lines):
                line_strip = line.strip()
                if any(kw in line_strip for kw in company_keywords):
                    # Check the line itself or the previous 1-2 lines
                    # Often format is:
                    # Company Name
                    # Role
                    # Date (Present)
                    search_range = lines[max(0, i-2):i+1]
                    for candidate_line in search_range:
                        c_strip = candidate_line.strip()
                        if 2 <= len(c_strip) <= 50 and not any(x in c_strip for x in ['-', '월', '년', 'Present']):
                            found_company = c_strip
                            break
                    if found_company: break
            
            if not found_company:
                # Fallback: Just take the first substantial line that doesn't look like name/contact
                for line in lines[:15]:
                    c_strip = line.strip()
                    if 2 <= len(c_strip) <= 40 and c_strip != name and '@' not in c_strip and '010' not in c_strip:
                        if any(x in c_strip for x in ['주식회사', '(주)', 'Inc', 'Corp', 'Team']):
                            found_company = c_strip
                            break

            if found_company:
                updates['current_company'] = found_company
        
        if updates:
            set_clause = ", ".join([f"{k} = ?" for k in updates.keys()])
            params = list(updates.values()) + [cid]
            cur.execute(f"UPDATE candidates SET {set_clause} WHERE id = ?", params)
            updated_count += 1
            if updated_count % 50 == 0:
                print(f'{updated_count}명 업데이트 완료...')

    conn.commit()
    print(f'\n최종 결과: 총 {updated_count}명의 후보자 정보 보강 완료')
    conn.close()

if __name__ == "__main__":
    backfill_missing_metadata()
