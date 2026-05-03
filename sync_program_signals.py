import json
import sqlite3
import requests
import os
import sys
from datetime import datetime

# ==========================================
# 1. 전형 단계별 및 드랍 사유별 신호 정의
# ==========================================
SIGNAL_MAP = {
    '최종합격': 1.0,
    '2차면접': 0.8,
    '1차면접': 0.6,
    '서류전형': 0.3,
    '지원포기': 0.1,
    '면접탈락': 0.2,
    '서류탈락': 0.0,
}

NEGATIVE_SIGNAL = {
    '역량부족': -0.3,
    '미스매치': -0.1,
    '처우조건불일치': 0.0,
    '포지션 마감': 0.0,
    '알수없음': 0.0,
}

# 설정 정보
SECRETS_PATH = 'secrets.json'
DB_PATH = os.environ.get('DB_PATH', 'candidates.db')
PROGRAM_DB_ID = "756285ea-c39e-4315-8530-8e4154488d03"

def get_notion_headers():
    if not os.path.exists(SECRETS_PATH):
        print(f"Error: {SECRETS_PATH} not found.")
        sys.exit(1)
    with open(SECRETS_PATH, 'r', encoding='utf-8') as f:
        secrets = json.load(f)
    return {
        "Authorization": f"Bearer {secrets['NOTION_API_KEY']}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }

# ==========================================
# 2. Database Schema 관리
# ==========================================
def ensure_schema():
    print(f"Checking schema for {DB_PATH}...")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 컬럼 존재 여부 확인
    cursor.execute("PRAGMA table_info(candidates)")
    columns = [row[1] for row in cursor.fetchall()]
    
    if 'program_signal' not in columns:
        print("Adding column: program_signal")
        cursor.execute("ALTER TABLE candidates ADD COLUMN program_signal REAL DEFAULT 0.0")
    
    if 'program_stage' not in columns:
        print("Adding column: program_stage")
        cursor.execute("ALTER TABLE candidates ADD COLUMN program_stage TEXT DEFAULT NULL")
    
    if 'program_position' not in columns:
        print("Adding column: program_position")
        cursor.execute("ALTER TABLE candidates ADD COLUMN program_position TEXT DEFAULT NULL")
    
    conn.commit()
    conn.close()

# ==========================================
# 3. 노션 데이터 로드 및 시그널 계산
# ==========================================
def fetch_program_data():
    headers = get_notion_headers()
    url = f"https://api.notion.com/v1/databases/{PROGRAM_DB_ID}/query"
    
    print("Fetching data from Notion PROGRAM DB (with pagination)...")
    
    all_results = []
    payload = {"page_size": 100}
    
    while True:
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code != 200:
            print(f"Error fetching Notion data: {response.text}")
            break
            
        data = response.json()
        all_results.extend(data.get('results', []))
        
        if not data.get('has_more'):
            break
        payload['start_cursor'] = data.get('next_cursor')
        print(f"  - Loaded {len(all_results)} entries, fetching next page...")

    parsed_data = []
    for page in all_results:
        props = page.get('properties', {})
        
        # 후보자 (title 타입)
        name_list = props.get('후보자', {}).get('title', [])
        name = name_list[0].get('plain_text', '').strip() if name_list else None
        
        # 전형 (status 타입)
        stage_obj = props.get('전형', {}).get('status', {})
        stage = stage_obj.get('name', '') if stage_obj else ''
        
        # 드랍사유 (select 타입)
        drop_obj = props.get('드랍사유', {}).get('select', {})
        drop_reason = drop_obj.get('name', '') if drop_obj else ''
        
        # 프로젝트 (포지션) (relation 타입)
        project_list = props.get('project', {}).get('relation', [])
        project_id = project_list[0].get('id') if project_list else None
        # 프로젝트 이름은 id로 나중에 fetch 하거나, 우선 id만 저장 (여기서는 간단히 id 저장 또는 추가 fetch 없이 빈값)
        # 만약 project_id가 있으면 "Position_{id}" 식의 임시 식별자 사용 가능
        # 또는 history_sync.py 처럼 notion.get_page(project_id)를 호출해야 함.
        # 성능을 위해 우선 project_id를 program_position으로 저장합니다.
        
        if name:
            # 기본 점수 계산
            base_score = SIGNAL_MAP.get(stage, 0.0)
            # 부정 신호 반영
            penalty = NEGATIVE_SIGNAL.get(drop_reason, 0.0)
            final_signal = max(0.0, min(1.0, base_score + penalty))
            
            parsed_data.append({
                'name': name,
                'stage': stage,
                'drop_reason': drop_reason,
                'signal': final_signal,
                'position': project_id
            })
            
    return parsed_data

# ==========================================
# 4. SQLite 업데이트 및 리포트
# ==========================================
def sync_signals():
    # 스키마 확인
    ensure_schema()
    
    # 데이터 로드
    program_data = fetch_program_data()
    if not program_data:
        print("No data to sync.")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    update_count = 0
    not_found = []
    
    print("\nUpdating candidates.db...")
    for item in program_data:
        name = item['name']
        signal = item['signal']
        stage = item['stage']
        position = item['position']
        
        # 이름 기반 매핑 (동명이인 고려 없이 우선 단순 업데이트)
        cursor.execute("""
            UPDATE candidates 
            SET program_signal = ?, program_stage = ?, program_position = ?
            WHERE name_kr = ?
        """, (signal, stage, position, name))
        
        if cursor.rowcount > 0:
            update_count += cursor.rowcount
            print(f"  [Match] {name} -> Stage: {stage}, Signal: {signal}, Pos: {position}")
        else:
            not_found.append(name)
            
    conn.commit()
    conn.close()
    
    # 5. 결과 리포트
    print("\n" + "="*40)
    print(" PROGRAM Feedback Loop Sync Report")
    print("="*40)
    print(f"Total entries processed: {len(program_data)}")
    print(f"Successfully matched & updated: {update_count}")
    print(f"Candidates not found in DB: {len(not_found)}")
    if not_found:
        print(f"  - Missing: {', '.join(not_found[:10])}{'...' if len(not_found) > 10 else ''}")
    print("="*40)

if __name__ == "__main__":
    sync_signals()
