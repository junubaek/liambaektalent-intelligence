import sqlite3
import json
import requests
import sys

sys.stdout.reconfigure(encoding='utf-8')

try:
    with open('secrets.json', 'r') as f:
        secrets = json.load(f)
    notion_key = secrets['NOTION_API_KEY']
except:
    print('Failed to load Notion Key')
    sys.exit(1)

con = sqlite3.connect('candidates.db')
c = con.cursor()
c.execute("SELECT id, name_kr, notion_url FROM candidates WHERE is_duplicate=0 AND notion_url IS NOT NULL AND (google_drive_url IS NULL OR google_drive_url = '') LIMIT 3")
rows = c.fetchall()

headers = {
    'Authorization': f'Bearer {notion_key}',
    'Notion-Version': '2022-06-28'
}

for r in rows:
    cid, name, n_url = r
    print(f'\n--- Candidate: {name} ({cid}) ---')
    print(f'Notion URL: {n_url}')
    
    parts = n_url.split('-')
    if len(parts) == 0: continue
    page_id_raw = parts[-1].split('?')[0]
    if len(page_id_raw) != 32:
        print('Invalid page ID from URL')
        continue
    page_id = f'{page_id_raw[:8]}-{page_id_raw[8:12]}-{page_id_raw[12:16]}-{page_id_raw[16:20]}-{page_id_raw[20:]}'
    
    resp = requests.get(f'https://api.notion.com/v1/pages/{page_id}', headers=headers)
    if resp.status_code != 200:
        print(f'API Error: {resp.status_code}')
        continue
        
    props = resp.json().get('properties', {})
    files = []
    urls = []
    
    for p_name, p_val in props.items():
        if p_val['type'] == 'files' and p_val['files']:
            for f in p_val['files']:
                files.append(f.get('name', 'Unamed file'))
        elif p_val['type'] == 'url' and p_val['url']:
            urls.append(p_val['url'])
            
    print(f'> Properties Files: {files}')
    print(f'> Properties URLs: {urls}')
    
    resp = requests.get(f'https://api.notion.com/v1/blocks/{page_id}/children', headers=headers)
    if resp.status_code == 200:
        blocks = resp.json().get('results', [])
        found_blocks = []
        for b in blocks:
            b_type = b.get('type')
            if b_type in ['file', 'pdf', 'bookmark', 'link_preview']:
                found_blocks.append(b_type)
        print(f'> Blocks inside page: Found {found_blocks}')
