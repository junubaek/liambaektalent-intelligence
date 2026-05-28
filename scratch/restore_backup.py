import shutil
import os
import sqlite3

backup_file = 'candidates_backup_20260526_1514.db'
target_file = 'candidates.db'

print(f"Restoring {backup_file} to {target_file}...")
shutil.copy(backup_file, target_file)
print("Restore complete.")

# Verify candidates in candidates.db
conn = sqlite3.connect(target_file)
cur = conn.cursor()
names = ['김국현','이원철','한상현']
cur.execute('''SELECT id, name_kr, sector, profile_summary, current_company
               FROM candidates WHERE name_kr IN (?, ?, ?) AND is_duplicate=0''', names)
for r in cur.fetchall():
    # Use ascii safe representation to avoid console CP949 errors
    print(f"Verified: {r[1]} | sector: {r[2]} | company: {r[4]}")
conn.close()
