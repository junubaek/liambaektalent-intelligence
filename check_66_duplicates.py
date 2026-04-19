import sqlite3
import pandas as pd

def main():
    conn = sqlite3.connect('candidates.db')
    c = conn.cursor()
    
    # Get the 66 missing candidates
    query_missing = """
    SELECT id, name_kr, email, phone 
    FROM candidates 
    WHERE is_duplicate=0 
    AND (google_drive_url IS NULL OR google_drive_url='' OR google_drive_url='#')
    """
    missing_cands = c.execute(query_missing).fetchall()
    
    # Get the rest of the candidates
    query_others = """
    SELECT id, name_kr, email, phone, google_drive_url 
    FROM candidates 
    WHERE is_duplicate=0
    AND (google_drive_url IS NOT NULL AND google_drive_url!='' AND google_drive_url!='#')
    """
    other_cands = c.execute(query_others).fetchall()
    
    duplicates_found = []
    
    for m_id, m_name, m_email, m_phone in missing_cands:
        if not m_name or len(m_name.strip()) < 2:
            continue
            
        m_name_clean = m_name.strip()
        m_email_clean = m_email.strip().lower() if m_email else ""
        m_phone_clean = m_phone.replace("-", "").replace(" ", "") if m_phone else ""
        
        for o_id, o_name, o_email, o_phone, o_drive in other_cands:
            if not o_name: continue
            o_name_clean = o_name.strip()
            o_email_clean = o_email.strip().lower() if o_email else ""
            o_phone_clean = o_phone.replace("-", "").replace(" ", "") if o_phone else ""
            
            is_dup = False
            match_reason = []
            
            # Rule 1: Exact Name + Email match
            if m_name_clean == o_name_clean and m_email_clean and o_email_clean and m_email_clean == o_email_clean:
                is_dup = True
                match_reason.append("이름+이메일 동일")
                
            # Rule 2: Exact Name + Phone match
            elif m_name_clean == o_name_clean and m_phone_clean and o_phone_clean and m_phone_clean == o_phone_clean:
                is_dup = True
                match_reason.append("이름+전화번호 동일")
                
            # Rule 3: Rare exact name match (Names with 3+ chars, or very distinct)
            elif m_name_clean == o_name_clean and len(m_name_clean) >= 3:
                # We'll flag it as potential
                # Exclude very common names if we had a list, but let's just log it
                is_dup = True
                match_reason.append("이름 완전 동일 (동명이인 의심)")
                
            if is_dup:
                duplicates_found.append({
                    'missing_name': m_name_clean,
                    'missing_id': m_id,
                    'matched_name': o_name_clean,
                    'matched_id': o_id,
                    'matched_drive': o_drive,
                    'reason': ", ".join(match_reason)
                })
                # Prevent matching the same missing candidate multiple times for logging simplicity
                break
                
    print(f"Total Missing Investigated: {len(missing_cands)}")
    print(f"Duplicates Found: {len(duplicates_found)}\n")
    
    for d in duplicates_found:
        print(f"[{d['reason']}] 누락자 '{d['missing_name']}' ({d['missing_id']}) == 기존 매칭자 '{d['matched_name']}' ({d['matched_id']})")

if __name__ == "__main__":
    main()
