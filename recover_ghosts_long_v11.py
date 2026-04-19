import sqlite3
import json
import re
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

def recover_ghost_long(task_info):
    r_id, text = task_info
    prompt = f"""당신은 전문 헤드헌터 데이터 추출 AI입니다. 아래 텍스트는 이력서 전문입니다. 
자기소개서가 앞에 길게 있어서 경력기술서가 맨 끝으로 밀려있거나, 영문 단락일 확률이 매우 높으니 끝까지 꼼꼼히 스캔하십시오.

[추출 규칙]
1. 연도(Date)나 기간이 명시되어 있지 않아도, 수행한 직무(Role), 업무내용(Responsibilities), 소속 기관(Company/Orgs)이 보이면 최대한 careers 배열에 포함.
2. 영문 이력서인 경우 뜻을 파악하여 careers 에 담을 것 (한글/영문 모두 허용).
3. 신입 지원자이거나, 내용이 완전히 파괴되어 유추가 도저히 불가능한 껍데기라면 careers는 빈 배열.

[JSON 출력 포맷]
{{
  "careers": [
    {{ "company": "회사명(없으면 미상)", "title": "직급/직무", "start_date": "YYYY-MM 또는 미상", "end_date": "미상/현재" }}
  ]
}}

[이력서 전문 (최대 13,000자)]
{text[:13000]}"""
    try:
        res = model.generate_content(prompt).text.strip()
        data = json.loads(res)
        car = json.dumps(data.get('careers', []), ensure_ascii=False)
        return r_id, car
    except Exception:
        return r_id, None

def get_namesake_position_long(task_info):
    r_id, text = task_info
    prompt = f"""이력서 전문을 보고, 이 지원자를 다른 동명이인과 식별할 수 있는 2~8글자 길이의 '핵심 직무 단어'(예: 프론트엔드, 의료연구, B2B마케팅, 자동화설비)를 생성하세요.
이력서 앞부분의 자기소개서를 건너뛰고, 문서 후반에 있을 경력 및 프로젝트 이력에서 핵심 단어를 찾아내세요.
만약 신입 지원자라면 '신입'이라고 출력하세요. 이력서 구조가 완전히 파괴되어 직무를 알 수 없는 껍데기 텍스트라면 빈 문자열("")을 출력하세요.
출력은 JSON 포맷 하나뿐입니다.

{{ "position": "문자열(2~8글자 또는 빈문자열)" }}

[이력서 전문 (최대 13,000자)]
{text[:13000]}"""
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

    print(f"[Phase 1] Scanning {len(rows)} ghosts with Top-to-Bottom Long Context Array...")
    with ThreadPoolExecutor(max_workers=5) as p:
        futures = {p.submit(recover_ghost_long, r): r for r in rows}
        for fut in tqdm(as_completed(futures), total=len(futures), desc="Long Context V11 Recovery"):
            r_id, car = fut.result()
            if car is not None and car != '[]' and len(car) > 5:
                c.execute("UPDATE candidates SET careers_json=? WHERE id=?", (car, r_id))
                success += 1
                if success % 10 == 0: conn.commit()
    conn.commit()
    print(f"[Phase 1] Recovered careers for {success} deep-hidden ghosts.")
    conn.close()

def run_namesake_renaming():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT name_kr FROM candidates WHERE name_kr NOT LIKE '%(%)' GROUP BY name_kr HAVING COUNT(*) > 1")
    namesakes = [row[0] for row in c.fetchall()]
    
    if not namesakes:
        print("[Phase 2] No namesakes found to rename.")
        conn.close()
        return

    q = ','.join(['?']*len(namesakes))
    c.execute(f"SELECT id, CAST(raw_text AS TEXT), name_kr FROM candidates WHERE name_kr IN ({q}) AND LENGTH(CAST(raw_text AS TEXT)) > 50", namesakes)
    rows = c.fetchall()
    
    print(f"[Phase 2] Renaming {len(namesakes)} groups ({len(rows)} candidates) via Long Context Position Extraction...")
    updates = 0
    with ThreadPoolExecutor(max_workers=5) as p:
        futures = {p.submit(get_namesake_position_long, (r[0], r[1])): r for r in rows}
        for fut in tqdm(as_completed(futures), total=len(futures), desc="Deep Namesake Checking"):
            r_id, pos = fut.result()
            r_info = futures[fut]
            old_name = r_info[2]
            
            clean_pos = str(pos).replace('(', '').replace(')', '').strip()
            if clean_pos:
                new_name = f"{old_name}({clean_pos})"
                c.execute("UPDATE candidates SET name_kr=? WHERE id=?", (new_name, r_id))
                updates += 1
                if updates % 10 == 0: conn.commit()
    conn.commit()
    conn.close()
    print(f"[Phase 2] Successfully appended (Position) to {updates} namesakes.")

if __name__ == "__main__":
    run_ghost_recovery()
    run_namesake_renaming()
