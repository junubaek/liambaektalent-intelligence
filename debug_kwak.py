# -*- coding: utf-8 -*-
import json
import pdfplumber
import requests

try:
    with open('secrets.json', 'r', encoding='utf-8') as f:
        s = json.load(f)
except Exception as e:
    print("Failed to load secrets:", e)
    s = {}

print('--- 1. NOTION API ---')
try:
    h = {'Authorization': 'Bearer ' + s.get('NOTION_API_KEY', ''), 'Notion-Version': '2022-06-28'}
    q = {'filter': {'property': '이름', 'title': {'contains': '곽창신'}}}
    r = requests.post(f"https://api.notion.com/v1/databases/{s.get('NOTION_DB_ID', '')}/query", headers=h, json=q).json()
    if r.get('results'):
        props = r['results'][0]['properties']
        print("간단프로필:", props.get('간단프로필', {}).get('rich_text', [{}])[0].get('plain_text') if props.get('간단프로필', {}).get('rich_text') else None)
        print("간단 프로필 요약:", props.get('간단 프로필 요약', {}).get('rich_text', [{}])[0].get('plain_text') if props.get('간단 프로필 요약', {}).get('rich_text') else None)
        print("Experience Summary:", props.get('Experience Summary', {}).get('rich_text', [{}])[0].get('plain_text') if props.get('Experience Summary', {}).get('rich_text') else None)
    else:
        print("No results found in Notion for 곽창신")
except Exception as e:
    print('Notion error:', e)

print('\n--- 2. PDFPLUMBER ---')
try:
    with pdfplumber.open(r'C:\Users\cazam\Downloads\02_resume 전처리\[42dot] 곽창신(자금)부문.pdf') as pdf:
        text = ''.join(page.extract_text() or '' for page in pdf.pages)
        print("Extracted chars:", len(text))
        print("Sample:", text[:200])
except Exception as e:
    print('PDF extract error:', e)

print('\n--- 3. CACHE JSON ---')
try:
    with open('candidates_cache_jd.json', 'r', encoding='utf-8') as f:
        c = json.load(f)
        kwak = [x for x in c if '곽창신' in x.get('name', x.get('이름', ''))]
        if kwak:
            print('Cache summary data:', kwak[0].get('summary', 'NONE'))
            print('Cache full data keys:', list(kwak[0].keys()))
        else:
            print('Kwak not found in cache.')
except Exception as e:
    print('Cache error:', e)
