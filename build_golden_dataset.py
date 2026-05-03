import json
import requests
import sys
import sqlite3
import os
from collections import defaultdict

# Set encoding for output
sys.stdout.reconfigure(encoding='utf-8')

# Load secrets
with open('secrets.json', 'r', encoding='utf-8') as f:
    s = json.load(f)

headers = {
    'Authorization': f'Bearer {s["NOTION_API_KEY"]}',
    'Notion-Version': '2022-06-28',
    'Content-Type': 'application/json'
}

DB_PATH = 'candidates.db'
PROJECT_DB_ID = '1ef4807f-4b58-4fec-ab66-5c2e593b1ca4'
PROGRAM_DB_ID = '756285ea-c39e-4315-8530-8e4154488d03'
OUTPUT_FILE = 'golden_dataset_v7.json'

GOOD_STAGES = {'최종합격', '2차면접', '1차면접', '서류전형'}

def fetch_all(db_id):
    url = f'https://api.notion.com/v1/databases/{db_id}/query'
    all_pages = []
    payload = {'page_size': 100}
    while True:
        r = requests.post(url, headers=headers, json=payload)
        if r.status_code != 200:
            print(f"Error fetching {db_id}: {r.text}")
            break
        data = r.json()
        all_pages.extend(data.get('results', []))
        if not data.get('has_more'):
            break
        payload['start_cursor'] = data.get('next_cursor')
    return all_pages

def build_golden_dataset():
    # 1. Fetch Projects (PID -> Position Name)
    print("Fetching Projects...")
    projects = fetch_all(PROJECT_DB_ID)
    pid_to_name = {}
    for p in projects:
        name_list = p.get('properties', {}).get('이름', {}).get('title', [])
        name = name_list[0].get('plain_text', '').strip() if name_list else ''
        if name:
            pid_to_name[p['id']] = name
    print(f"Loaded {len(pid_to_name)} positions.")

    # 2. Fetch Program data (Candidate + Stage + PID)
    print("Fetching Candidate Program data...")
    programs = fetch_all(PROGRAM_DB_ID)
    position_candidates = defaultdict(list)
    for page in programs:
        props = page.get('properties', {})
        name_list = props.get('후보자', {}).get('title', [])
        name = name_list[0].get('plain_text', '').strip() if name_list else ''
        stage = props.get('전형', {}).get('status', {}).get('name', '')
        proj_rel = props.get('PROJECT', {}).get('relation', [])
        
        if not name or not stage or not proj_rel:
            continue
        
        # 유효한 단계인지 확인
        if stage not in GOOD_STAGES:
            continue

        for proj in proj_rel:
            pid = proj.get('id', '')
            if pid in pid_to_name:
                pos_name = pid_to_name[pid]
                position_candidates[pos_name].append(name)

    # 3. Match Candidate Names to SQLite UUIDs
    print("Matching names to SQLite IDs...")
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    # 한번에 모든 후보자 매핑 정보 가져오기
    all_names = set()
    for names in position_candidates.values():
        all_names.update(names)
    
    name_to_id = {}
    if all_names:
        placeholders = ','.join(['?'] * len(all_names))
        cur.execute(f"SELECT name_kr, id FROM candidates WHERE name_kr IN ({placeholders})", list(all_names))
        for r_name, r_id in cur.fetchall():
            name_to_id[r_name] = r_id
    conn.close()

    # 4. Build Final Dataset
    dataset = []
    print("\nFinal Golden Dataset v7 Summary:")
    for pos_name, candidate_names in position_candidates.items():
        relevant_ids = []
        found_names = []
        for name in set(candidate_names): # 중복 제거
            if name in name_to_id:
                relevant_ids.append(name_to_id[name])
                found_names.append(name)
        

        if relevant_ids:
            dataset.append({
                "query": pos_name,
                "relevant_ids": relevant_ids,
                "relevant_names": found_names
            })
            print(f"  - [{pos_name}] Queries: {len(relevant_ids)} candidates matched.")

    # 5. Save
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(dataset, f, ensure_ascii=False, indent=2)
    
    print(f"\nSuccessfully created {OUTPUT_FILE} with {len(dataset)} position queries.")

if __name__ == "__main__":
    build_golden_dataset()
