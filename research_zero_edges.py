import sqlite3
import json
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('processed_step6.json', 'r', encoding='utf-8') as f:
    d = json.load(f)

zero_uids = [uid for uid, v in d.items() if v.get('edge_count', 0) == 0]

db = sqlite3.connect('candidates.db')
c = db.cursor()

names_map = {}
for uid in zero_uids:
    c.execute('SELECT name_kr FROM candidates WHERE id=?', (uid,))
    row = c.fetchone()
    if row:
        names_map[row[0]] = uid

folder = r'C:\Users\cazam\Downloads\02_resume_converted_v8'
if not os.path.exists(folder):
    print("Folder does not exist")
    sys.exit(1)

files = os.listdir(folder)

matched_uids = []
matched_names = []
matched_files = []

for name, uid in names_map.items():
    for f in files:
        if name in f and f.endswith('.docx'):
            matched_uids.append(uid)
            matched_names.append(name)
            matched_files.append(os.path.join(folder, f))
            break

print(f"Total zero edge candidates: {len(zero_uids)}")
print(f"Candidates with .docx files in v8 folder: {len(matched_uids)}")
print(f"Names: {matched_names[:10]}")
