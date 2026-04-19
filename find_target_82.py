
import sqlite3, os, re

conn = sqlite3.connect(r'c:\Users\cazam\Downloads\이력서자동분석검색시스템\candidates.db')
c = conn.cursor()
c.execute('SELECT name_kr FROM candidates WHERE name_kr IS NOT NULL')
db_names_raw = [r[0] for r in c.fetchall()]

def clean_name(n):
    if not n: return ''
    n = n.split('(')[0]
    return re.sub(r'[^가-힣A-Za-z]', '', n).strip()

db_names_clean = {clean_name(n) for n in db_names_raw}

d = r'C:\Users\cazam\Downloads\02_resume 전처리'
possible_new_files = []

for f in os.listdir(d):
    if f.startswith('~$') or not (f.endswith('.pdf') or f.endswith('.doc') or f.endswith('.docx')): continue
    
    b = os.path.splitext(f)[0]
    # parse out the name from filename
    # Usually: [Company]Name_Role or [Company]Name(Role) or [Company] Name (Role)
    name_str = b
    if ']' in name_cand:=name_str: name_cand = name_cand.split(']')[-1].strip()
    name_cand = name_cand.split('(')[0].strip()
    
    parts = name_cand.split('_')
    for p in parts:
        pc = clean_name(p)
        if 2 <= len(pc) <= 4 and re.match(r'^[가-힣]+$', pc):
            name_cand = pc
            break
            
    c_name = clean_name(name_cand)
    if not c_name: c_name = clean_name(b)
    
    # Very loose match
    matched = False
    for dn in db_names_clean:
        if c_name == dn or (len(c_name)>=2 and c_name in dn) or (len(dn)>=2 and dn in c_name):
            matched = True
            break
            
    if not matched: possible_new_files.append((f, c_name))

print(f'Total Unmatched Files by Name: {len(possible_new_files)}')

import datetime
if possible_new_files:
    # Sort by mtime
    possible_new_files.sort(key=lambda x: os.path.getmtime(os.path.join(d, x[0])), reverse=True)
    for f, c in possible_new_files[:10]:
        t = datetime.datetime.fromtimestamp(os.path.getmtime(os.path.join(d, f))).strftime('%Y-%m-%d %H:%M')
        print(f'{f} ({t}) -> {c}')

