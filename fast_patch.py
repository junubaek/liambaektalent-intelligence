import json
import pdfplumber
import re
import os

with open('candidates_cache_jd.json', 'r', encoding='utf-8') as f:
    c = json.load(f)

kwak = None
for x in c:
    if '곽창신' in x.get('name',''):
        kwak = x
        break

if kwak:
    print('Original Sector in Cache:', kwak.get('main_sectors'))
    try:
        with pdfplumber.open(r'C:\Users\cazam\Downloads\02_resume 전처리\[42dot] 곽창신(자금)부문.pdf') as pdf:
            text = ''.join(page.extract_text() or '' for page in pdf.pages[:2])
            keywords = ['경력', '주요업무', '간단프로필', 'Career', 'Experience', '업무경험']
            start_idx = -1
            for kw in keywords:
                idx = text.find(kw)
                if idx != -1 and (start_idx == -1 or idx < start_idx):
                    start_idx = idx
            
            if start_idx != -1:
                text = text[start_idx:]
            else:
                text = re.sub(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', '', text)
                text = re.sub(r'\d{2,3}[-\.\s]\d{3,4}[-\.\s]\d{4}', '', text)
                
            kwak['summary'] = ' '.join(text.split())[:500]
            print("NEW SUMMARY:", kwak['summary'])
    except Exception as e:
        print("PDF ERROR:", e)

    with open('candidates_cache_jd.json', 'w', encoding='utf-8') as f:
        json.dump(c, f, ensure_ascii=False, indent=2)
    print('Updated Kwak summary successfully!')
