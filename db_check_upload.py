import sqlite3
import subprocess
import json
import time

# 1. Check local DB counts
print("=== 1. Local DB Counts ===")
conn = sqlite3.connect('candidates.db')
cur = conn.cursor()
cur.execute('SELECT COUNT(*) FROM candidates')
print(f'전체: {cur.fetchone()[0]}명')
cur.execute('SELECT COUNT(*) FROM candidates WHERE is_duplicate=0')
print(f'활성(is_duplicate=0): {cur.fetchone()[0]}명')
cur.execute('SELECT COUNT(*) FROM candidates WHERE is_duplicate=1')
print(f'중복(is_duplicate=1): {cur.fetchone()[0]}명')
conn.close()

# 2. Run scratch_upload_db.py
print("\n=== 2. Running scratch_upload_db.py ===")
result = subprocess.run(['python', 'scratch_upload_db.py'], capture_output=True, text=True)
print("STDOUT:", result.stdout)
print("STDERR:", result.stderr)

# 3. Check Google Drive metadata
print("\n=== 3. Google Drive Metadata ===")
from connectors.gdrive_api import GDriveConnector
gdrive = GDriveConnector()
res = gdrive.service.files().get(
    fileId='1q2LHW3EF2_IK_5gPjhiUAzGASjvjCQ0E',
    fields='name, size, modifiedTime'
).execute()
print(res)
