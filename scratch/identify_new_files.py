import os
import sqlite3
import hashlib
import sys

# Set encoding for output
if sys.stdout.encoding != 'utf-8':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

resume_dir = r'C:\Users\cazam\Downloads\02_resume 전처리'
conn = sqlite3.connect('candidates.db')
cur = conn.cursor()

# Get existing hashes
cur.execute('SELECT document_hash FROM candidates WHERE document_hash IS NOT NULL')
existing_hashes = set(r[0] for r in cur.fetchall())
conn.close()

def calculate_hash(filepath):
    sha256_hash = hashlib.sha256()
    with open(filepath, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

all_files = []
for f in os.listdir(resume_dir):
    if f.lower().endswith(('.pdf', '.docx', '.doc')):
        all_files.append(f)

new_files = []
for f in all_files:
    path = os.path.join(resume_dir, f)
    try:
        f_hash = calculate_hash(path)
        if f_hash not in existing_hashes:
            new_files.append((f, f_hash))
    except Exception as e:
        print(f"Error hashing {f}: {e}")

print(f'전체 파일: {len(all_files)}개')
print(f'이미 처리됨 (DB 기반): {len(existing_hashes)}개')
print(f'신규 파일 (해시 기준): {len(new_files)}개')

for f, h in new_files[:20]:
    print(f'  {f} ({h[:8]})')

# Save new files list for processing
import json
with open('new_files_to_process.json', 'w', encoding='utf-8') as f:
    json.dump(new_files, f, indent=2, ensure_ascii=False)
