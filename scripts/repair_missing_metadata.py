import sqlite3, os, json, re
from google import genai
from google.genai import types

# Load secrets
SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPTS_DIR)
with open(os.path.join(PROJECT_ROOT, "secrets.json"), "r", encoding="utf-8") as f:
    secrets = json.load(f)

client = genai.Client(api_key=secrets["GEMINI_API_KEY"])
DB_PATH = os.environ.get('DB_PATH', 'candidates.db')

from concurrent.futures import ThreadPoolExecutor

def repair_single_candidate(row, cur_conn):
    cid, name_kr, raw_text = row
    print(f"[*] Analyzing {name_kr or cid}...")
    
    system_prompt = """당신은 리크루팅 전문 AI입니다. 제공된 이력서 텍스트에서 다음 정보를 정확히 추출하여 JSON으로 반환하세요.
    1. name: 한국어 이름 (없으면 비움)
    2. current_company: 현재 혹은 가장 최근 직장명 (없으면 '미상')
    3. seniority: 전체 경력 연수 (숫자만, 예: 5.5)
    4. education: 학력 리스트 (school, major, degree, graduation_year 포함)
    """
    
    try:
        config = types.GenerateContentConfig(
            response_mime_type="application/json",
            system_instruction=system_prompt,
            response_schema={
                "type": "OBJECT",
                "properties": {
                    "name": {"type": "STRING"},
                    "current_company": {"type": "STRING"},
                    "seniority": {"type": "NUMBER"},
                    "education": {
                        "type": "ARRAY",
                        "items": {
                            "type": "OBJECT",
                            "properties": {
                                "school": {"type": "STRING"},
                                "major": {"type": "STRING"},
                                "degree": {"type": "STRING"},
                                "graduation_year": {"type": "STRING"}
                            }
                        }
                    }
                }
            }
        )
        
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[f"이력서 텍스트:\n{raw_text[:4000]}"],
            config=config
        )
        
        data = json.loads(response.text)
        
        # We need a new connection per thread for safety
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        
        updates = []
        params = []
        
        if data.get("name") and (not name_kr or name_kr.lower() == "unknown"):
            updates.append("name_kr = ?")
            params.append(data["name"])
            
        if data.get("current_company") and data["current_company"] != "미상":
            updates.append("current_company = ?")
            params.append(data["current_company"])
            
        if data.get("seniority") is not None:
            updates.append("total_years = ?")
            params.append(float(data["seniority"]))
            
        if data.get("education"):
            updates.append("education_json = ?")
            params.append(json.dumps(data["education"], ensure_ascii=False))
        
        if updates:
            params.append(cid)
            sql = f"UPDATE candidates SET {', '.join(updates)} WHERE id = ?"
            cur.execute(sql, params)
            conn.commit()
            print(f"  [OK] Updated {data.get('name') or name_kr or cid}")
        else:
            print(f"  [SKIP] No new info for {name_kr or cid}")
        conn.close()
            
    except Exception as e:
        print(f"  [ERROR] Analyzing {cid}")

def repair_candidates(limit=50):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    cur.execute('''
        SELECT id, name_kr, raw_text 
        FROM candidates 
        WHERE ((current_company="미상" OR current_company IS NULL OR name_kr="Unknown" OR name_kr IS NULL)
               OR (education_json="[]" OR education_json IS NULL))
          AND raw_text IS NOT NULL 
          AND length(raw_text) > 200
        LIMIT ?
    ''', (limit,))
    
    rows = cur.fetchall()
    conn.close()
    
    print(f"[*] Starting parallel repair for {len(rows)} candidates...")
    
    with ThreadPoolExecutor(max_workers=5) as executor:
        executor.map(lambda r: repair_single_candidate(r, None), rows)
    
    print("[*] Batch Repair complete.")

if __name__ == "__main__":
    repair_candidates(50)
