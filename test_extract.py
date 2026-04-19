
from docx import Document
import os

path = r'C:\Users\cazam\Downloads\02_resume_converted_v8\김시형(총무팀 자산관리)부문_원본.docx'
if os.path.exists(path):
    doc = Document(path)
    text = '\n'.join([p.text for p in doc.paragraphs])
    with open('test_extract.txt', 'w', encoding='utf-8') as f:
        f.write(text)
    print(f"Extraction successful. Length: {len(text)}")
else:
    print("File not found")
