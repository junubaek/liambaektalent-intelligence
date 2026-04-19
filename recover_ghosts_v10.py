import sqlite3
import json
import re
import traceback
import google.generativeai as genai
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm

with open("secrets.json", "r", encoding="utf-8") as f:
    secrets = json.load(f)
genai.configure(api_key=secrets.get("GEMINI_API_KEY", ""))

model = genai.GenerativeModel(
    'gemini-2.5-flash-lite',
    generation_config={"response_mime_type": "application/json"}
)

DB_PATH = r"c:\Users\cazam\Downloads\이력서자동분석검색시스템\candidates.db"

def recover_ghost(task_info):
    r_id, text = task_info
    prompt = f"""당신은 전문 헤드헌터 파서입니다. 이력서를 분석해 명확한 팩트를 JSON으로 추출하되, 규칙이 있습니다:
1. 연도(Date)나 기간이 명시되어 있지 않아도 직무(Role), 소속(Company)이 유추되면 최대한 careers 배열에 포함.
2. 영문 이력서일 경우 내용 해석 요약하여 careers 에 담을 것.
3. 신입 지원자이거나 내용이 없다면 careers는 빈 배열.

[JSON 출력 포맷]
{{
  "careers": [
    {{ "company": "회사명(없으면 미상)", "title": "직급/직무", "start_date": "YYYY-MM 또는 미상", "end_date": "미상/현재" }}
  ]
}}

[이력서 원문]
{text[:4000]}"""
    try:
        res = model.generate_content(prompt).text.strip()
        data = json.loads(res)
        car = json.dumps(data.get('careers', []), ensure_ascii=False)
        return r_id, car
    except Exception:
        return r_id, None

def get_namesake_position(task_info):
    r_id, text = task_info
    prompt = f"""아래 이력서 텍스트를 보고, 이 지원자를 식별할 수 있는 2~7글자 길이의 '핵심 직무 키워드'를 생성하세요. 
만약 신입 지원자라면 '신입'이라고 출력하세요. 이력서 구조가 파괴되어 직무를 알 수 없는 껍데기 텍스트라면 빈 문자열을 출력하세요.
출력은 JSON 포맷입니다.

{{ "position": "문자열" }}

[이력서 텍스트]
{text[:2500]}"""
    try:
        res = model.generate_content(prompt).text.strip()
        data = json.loads(res)
        return r_id, data.get('position', '')
    except:
        return r_id, ""

def run_ghost_recovery():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id, CAST(raw_text AS TEXT) FROM candidates WHERE (careers_json IS NULL OR careers_json='[]' OR careers_json='') AND LENGTH(CAST(raw_text AS TEXT)) >= 100")
    rows = c.fetchall()
    
    success = 0
    if not rows:
        print("[Phase 1] No ghost candidates left to recover.")
        conn.close()
        return

    with ThreadPoolExecutor(max_workers=5) as p:
        futures = {p.submit(recover_ghost, r): r for r in rows}
        for fut in tqdm(as_completed(futures), total=len(futures), desc="Deep Ghost Recovery"):
            r_id, car = fut.result()
            if car is not None and car != '[]' and len(car) > 5:
                c.execute("UPDATE candidates SET careers_json=? WHERE id=?", (car, r_id))
                success += 1
                if success % 20 == 0: conn.commit()
    conn.commit()
    print(f"[Phase 1] Recovered careers for {success} ghosts.")
    conn.close()

def run_namesake_renaming():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    # Find all name_kr having > 1
    c.execute("SELECT name_kr FROM candidates WHERE name_kr NOT LIKE '%(%)' GROUP BY name_kr HAVING COUNT(*) > 1")
    namesakes = [row[0] for row in c.fetchall()]
    
    if not namesakes:
        print("[Phase 2] No namesakes found to rename.")
        conn.close()
        return

    q = ','.join(['?']*len(namesakes))
    c.execute(f"SELECT id, CAST(raw_text AS TEXT), name_kr FROM candidates WHERE name_kr IN ({q}) AND LENGTH(CAST(raw_text AS TEXT)) > 50", namesakes)
    rows = c.fetchall()
    
    updates = 0
    with ThreadPoolExecutor(max_workers=5) as p:
        futures = {p.submit(get_namesake_position, (r[0], r[1])): r for r in rows}
        for fut in tqdm(as_completed(futures), total=len(futures), desc="Namesake Renaming"):
            r_id, pos = fut.result()
            r_info = futures[fut]
            old_name = r_info[2]
            
            clean_pos = str(pos).replace('(', '').replace(')', '').strip()
            if clean_pos:
                new_name = f"{old_name}({clean_pos})"
                c.execute("UPDATE candidates SET name_kr=? WHERE id=?", (new_name, r_id))
                updates += 1
                if updates % 20 == 0: conn.commit()
    conn.commit()
    conn.close()
    print(f"[Phase 2] Renamed {updates} namesakes.")

if __name__ == "__main__":
    run_ghost_recovery()
    run_namesake_renaming()
