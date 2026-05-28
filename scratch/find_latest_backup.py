import os
import sqlite3
import re

backups = [f for f in os.listdir('.') if re.match(r'candidates_backup_\d{8}_\d{4}\.db', f)]
backups.sort(reverse=True)

print("Timestamped backups found:")
for b in backups:
    print(f"  {b}")
    
if backups:
    latest = backups[0]
    print(f"\nChecking latest timestamped backup: {latest}")
    conn = sqlite3.connect(latest)
    cur = conn.cursor()
    
    # Check columns
    cur.execute("PRAGMA table_info(candidates)")
    cols = [x[1] for x in cur.fetchall()]
    print("Columns:", cols)
    
    # Verify candidates
    names = ['김국현','이원철','한상현']
    q_fields = ['id', 'name_kr', 'current_company']
    if 'sector' in cols:
        q_fields.append('sector')
    if 'profile_summary' in cols:
        q_fields.append('profile_summary')
        
    select_fields = ", ".join(q_fields)
    
    query = f"SELECT {select_fields} FROM candidates WHERE name_kr IN (?, ?, ?) AND is_duplicate=0"
    cur.execute(query, names)
    for r in cur.fetchall():
        print(f"Found: {r}")
        
    conn.close()
