
import os, json, hashlib, zipfile
import xml.etree.ElementTree as ET
import fitz

def read_docx(path):
    try:
        doc = zipfile.ZipFile(path)
        return ''.join(n.text for n in ET.fromstring(doc.read('word/document.xml')).iter() if n.text)
    except: return ''

def read_doc_text(path):
    f = f.lower()
    t = ''
    try:
        if path.endswith('.pdf'):
            d = fitz.open(path)
            for p in d: t += p.get_text()
        elif path.endswith('.docx') or path.endswith('.doc'):
            t = read_docx(path)
    except: pass
    return t.strip()

processed_hashes = set()
with open(r'c:\Users\cazam\Downloads\이력서자동분석검색시스템\processed.json', 'r', encoding='utf-8') as f:
    d = json.load(f)
    for v in d.values():
        if isinstance(v, dict) and 'text_hash' in v: processed_hashes.add(v['text_hash'])

new_files = []
d = r'C:\Users\cazam\Downloads\02_resume 전처리'
for f in os.listdir(d):
    if f.startswith('~$'): continue
    if f.endswith('.pdf') or f.endswith('.docx') or f.endswith('.doc'):
        p = os.path.join(d, f)
        t = read_doc_text(p)
        if len(t)<50: continue
        h = hashlib.md5(t.encode('utf-8')).hexdigest()
        if h not in processed_hashes:
            new_files.append((f, h))

print(f'Total uniquely new files by hash: {len(new_files)}')

