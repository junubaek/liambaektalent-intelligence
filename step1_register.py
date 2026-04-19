import sqlite3
import json
import os
import uuid
from datetime import datetime

# DB Schema reference from previous output:
# id, name_kr, email, phone, raw_text, document_hash, is_parsed, is_neo4j_synced, is_pinecone_synced, last_error, created_at, updated_at, birth_year, education_json, careers_json

conn = sqlite3.connect(r'C:\Users\cazam\Downloads\이력서자동분석검색시스템\candidates.db')
c = conn.cursor()

c.execute("SELECT phone FROM candidates WHERE phone IS NOT NULL AND phone != ''")
db_phones = set([row[0].replace('-', '').replace(' ', '') for row in c.fetchall()])

with open(r'C:\Users\cazam\Downloads\이력서자동분석검색시스템\missing_files_report.json', 'r', encoding='utf-8') as f:
    report = json.load(f)

unmatched = report.get('unmatched_list', [])
new_resumes = []

for u in unmatched:
    phone = u.get('extracted_phone')
    if phone and phone not in db_phones:
        new_resumes.append(u)

print(f"Total new resumes to register: {len(new_resumes)}")

# 1. 파일 찾기 및 raw_text 추출
FOLDER_V8 = r"C:\Users\cazam\Downloads\02_resume_converted_v8"
FOLDER_PRE = r"C:\Users\cazam\Downloads\02_resume 전처리"

all_files = {}
if os.path.exists(FOLDER_PRE):
    for f in os.listdir(FOLDER_PRE):
        if f.endswith(('.pdf', '.docx', '.doc')):
            base = f.rsplit('.', 1)[0]
            all_files[base] = os.path.join(FOLDER_PRE, f)
            
if os.path.exists(FOLDER_V8):
    for f in os.listdir(FOLDER_V8):
        if f.endswith('.docx'):
            base = f.rsplit('.', 1)[0]
            all_files[base] = os.path.join(FOLDER_V8, f)

import hashlib
import pdfplumber
from docx import Document

def extract_text_natively(filepath):
    ext = filepath.rsplit(".", 1)[-1].lower()
    try:
        if ext == "pdf":
            with pdfplumber.open(filepath) as pdf:
                return "\n".join(p.extract_text() or "" for p in pdf.pages)
        elif ext in ("docx"):
            doc = Document(filepath)
            return "\n".join(p.text for p in doc.paragraphs)
    except Exception as e:
        return ""
    return ""

inserted = 0
for r in new_resumes:
    base_name = r['file']
    if base_name in all_files:
        filepath = all_files[base_name]
        text = extract_text_natively(filepath)
        if len(text) > 100:
            doc_hash = hashlib.sha256(text.encode('utf-8')).hexdigest()
            new_id = str(uuid.uuid4())
            now = datetime.now().isoformat()
            
            try:
                c.execute("""
                    INSERT INTO candidates (id, name_kr, phone, email, raw_text, document_hash, is_parsed, is_neo4j_synced, is_pinecone_synced, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, 0, 0, 0, ?, ?)
                """, (new_id, r['name_kr'], r['extracted_phone'], '', text, doc_hash, now, now))
                inserted += 1
            except Exception as e:
                print(f"Failed to insert {r['name_kr']}: {e}")

conn.commit()

c.execute("SELECT COUNT(*) FROM candidates")
print(f"Total candidates after insertion: {c.fetchone()[0]}")

conn.close()
