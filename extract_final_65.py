import sqlite3
import json

db = sqlite3.connect('candidates.db')

# 1. Update the duplicate 'Kim Sang Hyun'
dup_id = "73e951f3-c172-4bd9-b338-d5d6129e1c28"
db.execute("UPDATE candidates SET is_duplicate=1 WHERE id=?", (dup_id,))
db.commit()

# 2. Get the remaining 65 names
query = """
SELECT name_kr 
FROM candidates 
WHERE is_duplicate=0 
AND (google_drive_url IS NULL OR google_drive_url='' OR google_drive_url='#')
"""
res = db.execute(query).fetchall()

names = [r[0] if r[0] else '이름없음' for r in res]
print('Found:', len(names))
print(', '.join(names))
