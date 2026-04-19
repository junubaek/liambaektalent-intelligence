import sqlite3

def clean_txt(t): return t.strip().lower() if t else ""
def clean_ph(t): return t.replace('-', '').replace(' ', '') if t else ""

conn = sqlite3.connect('candidates.db')
query_m = "SELECT id, name_kr, email, phone FROM candidates WHERE is_duplicate=0 AND (google_drive_url IS NULL OR google_drive_url='' OR google_drive_url='#')"
missing = conn.execute(query_m).fetchall()

query_o = "SELECT id, name_kr, email, phone FROM candidates WHERE is_duplicate=0 AND google_drive_url IS NOT NULL AND google_drive_url!='' AND google_drive_url!='#'"
others = conn.execute(query_o).fetchall()

dups = []
for m_id, m_name, m_email, m_phone in missing:
    me = clean_txt(m_email)
    mp = clean_ph(m_phone)
    if not me and not mp: continue
    
    for o_id, o_name, o_email, o_phone in others:
        oe = clean_txt(o_email)
        op = clean_ph(o_phone)
        
        reason = []
        if me and oe and me == oe: reason.append("이메일 동일")
        if mp and op and len(mp)>8 and mp == op: reason.append("휴대폰 동일")
        
        if reason:
            dups.append(f"[{', '.join(reason)}] {m_name} ({m_id}) == {o_name} ({o_id})")
            break

print(f"Loose Duplicates Found: {len(dups)}\n" + "\n".join(dups))
