import sqlite3
import json
import re
import traceback
import google.generativeai as genai
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
import time

with open("secrets.json", "r", encoding="utf-8") as f:
    secrets = json.load(f)
genai.configure(api_key=secrets.get("GEMINI_API_KEY", ""))

model = genai.GenerativeModel(
    'gemini-2.5-flash-lite',
    generation_config={"response_mime_type": "application/json"}
)

DB_PATH = r"c:\Users\cazam\Downloads\이력서자동분석검색시스템\candidates.db"

# ---------------------------------------------------------
# Phase 1: Identity Repair
# ---------------------------------------------------------
def get_real_name(task_info):
    r_id, old_name, text = task_info
    prompt = f"""다음 이력서 텍스트에서 지원자의 '본명(한글 이름)' 한 단어만 식별하세요. 출력은 아래 JSON 포맷에 맞춥니다.
{{ "name_kr": "홍길동" }}

[이력서 텍스트]
{text[:1000]}"""
    try:
        res = model.generate_content(prompt).text.strip()
        data = json.loads(res)
        name = data.get("name_kr", "")
        clean_name = re.sub(r'[^가-힣A-Za-z]', '', name)
        if 2 <= len(clean_name) <= 10 and clean_name != old_name:
            return r_id, clean_name
    except: pass
    return r_id, None

# ---------------------------------------------------------
# Phase 2: Metadata Backfill
# ---------------------------------------------------------
def extract_metadata(task_info):
    r_id, text = task_info
    prompt = f"""당신은 전문 헤드헌터 파서입니다. 이력서를 분석해 명확한 팩트만 JSON으로 추출하세요.
{{
  "birth_year": 정수 (예: 1985. 없으면 null),
  "education": [
    {{ "school": "학교명", "major": "전공", "degree": "학위", "graduation_year": "졸업연도" }}
  ],
  "careers": [
    {{ "company": "회사명", "title": "직급/직무", "start_date": "YYYY-MM", "end_date": "YYYY-MM 또는 현재" }}
  ]
}}

[이력서 원문]
{text[:6000]}"""
    try:
        res = model.generate_content(prompt).text.strip()
        data = json.loads(res)
        b_year = data.get('birth_year')
        edu = json.dumps(data.get('education', []), ensure_ascii=False)
        car = json.dumps(data.get('careers', []), ensure_ascii=False)
        return r_id, b_year, edu, car
    except Exception as e:
        return r_id, None, None, None

# ---------------------------------------------------------
# Runners
# ---------------------------------------------------------
def run_identity_repair():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    # 5명 이상 동일 이름인 행 색출
    c.execute("SELECT name_kr FROM candidates GROUP BY name_kr HAVING COUNT(*) >= 4")
    suspicious_names = [row[0] for row in c.fetchall()]
    
    if not suspicious_names:
        print("[Phase 1] No high-collision names found.")
        return
        
    print(f"[Phase 1] Found {len(suspicious_names)} suspicious name groups (e.g. {suspicious_names[:5]}). Repairing...")
    
    q = ','.join(['?']*len(suspicious_names))
    c.execute(f"SELECT id, name_kr, CAST(raw_text AS TEXT) FROM candidates WHERE name_kr IN ({q}) AND LENGTH(CAST(raw_text AS TEXT)) > 100", suspicious_names)
    rows = c.fetchall()
    
    updates = 0
    with ThreadPoolExecutor(max_workers=5) as p:
        futures = {p.submit(get_real_name, r): r for r in rows}
        for fut in tqdm(as_completed(futures), total=len(futures), desc="Fixing Names"):
            r_id, new_name = fut.result()
            if new_name:
                c.execute("UPDATE candidates SET name_kr = ? WHERE id = ?", (new_name, r_id))
                updates += 1
                if updates % 20 == 0: conn.commit()
    conn.commit()
    conn.close()
    print(f"[Phase 1] Fixed {updates} identity collisions.\n")

def run_metadata_backfill():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id, CAST(raw_text AS TEXT) FROM candidates WHERE (careers_json IS NULL OR careers_json='[]' OR careers_json='') AND LENGTH(CAST(raw_text AS TEXT)) > 100")
    rows = c.fetchall()
    
    if not rows:
        print("[Phase 2] No missing metadata rows found.")
        return
        
    print(f"[Phase 2] Backfilling metadata for {len(rows)} candidates...")
    
    success = 0
    with ThreadPoolExecutor(max_workers=5) as p:
        futures = {p.submit(extract_metadata, r): r for r in rows}
        for fut in tqdm(as_completed(futures), total=len(futures), desc="Backfill JSON"):
            r_id, b_year, edu, car = fut.result()
            if car is not None:
                c.execute("UPDATE candidates SET birth_year=?, education_json=?, careers_json=? WHERE id=?", (b_year, edu, car, r_id))
                success += 1
                if success % 20 == 0: conn.commit()
                
    conn.commit()
    conn.close()
    print(f"[Phase 2] Successfully backfilled {success} candidates.")

if __name__ == "__main__":
    run_identity_repair()
    time.sleep(2)
    run_metadata_backfill()
    print("\n✅ V8.9 Backfill Completed Successfully!")
