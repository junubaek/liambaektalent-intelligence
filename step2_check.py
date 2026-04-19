import json
import os
import sqlite3
import pdfplumber
from docx import Document

print('--- Step 2: 499건 판독 보류 조사 ---')

with open(r'C:\Users\cazam\Downloads\이력서자동분석검색시스템\missing_files_report.json', 'r', encoding='utf-8') as f:
    report = json.load(f)

unmatched = report.get('unmatched_list', [])

conn = sqlite3.connect(r'C:\Users\cazam\Downloads\이력서자동분석검색시스템\candidates.db')
conn.row_factory = sqlite3.Row
c = conn.cursor()

c.execute("SELECT phone FROM candidates WHERE phone IS NOT NULL AND phone != ''")
db_phones = set([row[0].replace('-', '').replace(' ', '') for row in c.fetchall()])

c.execute("SELECT id, name_kr FROM candidates")
db_names = {}
for row in c.fetchall():
    db_names.setdefault(row['name_kr'], []).append(row['id'])

no_phone_files = []
for u in unmatched:
    phone = u.get('extracted_phone')
    if not phone:
        no_phone_files.append(u)
        
print(f"Total 판독 보류 파일 (연락처 없음): {len(no_phone_files)}건")

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

def extract_text(filepath):
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

img_pdf_count = 0
text_success_count = 0
mapped_by_name = 0

for u in no_phone_files:
    base_name = u['file']
    name_kr = u['name_kr']
    if base_name in all_files:
        fp = all_files[base_name]
        text = extract_text(fp)
        if len(text) < 100:
            img_pdf_count += 1
        else:
            text_success_count += 1
            if name_kr in db_names:
                mapped_by_name += 1
                
print(f"텍스트 추출 시 100자 미만 (이미지 PDF 등): {img_pdf_count}건")
print(f"텍스트 전처리 성공 (정상 이력서): {text_success_count}건")
print(f"  └ 이미지 제외, 텍스트 성공분 중 이름 매칭 재시도 성공: {mapped_by_name}건")
