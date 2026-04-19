import sqlite3

db = sqlite3.connect('candidates.db')
res = db.execute('''
    SELECT name_kr 
    FROM candidates 
    WHERE is_duplicate=0 
    AND (google_drive_url IS NULL OR google_drive_url="" OR google_drive_url="#")
''').fetchall()

names = [r[0] if r[0] else '이름없음' for r in res]
print(', '.join(names))
