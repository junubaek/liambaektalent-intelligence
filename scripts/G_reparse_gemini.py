import sqlite3
import json
import time
import os
import google.generativeai as genai
from datetime import datetime

def setup_gemini():
    with open("secrets.json", "r") as f:
        secrets = json.load(f)
    genai.configure(api_key=secrets.get("GEMINI_API_KEY"))
    return genai.GenerativeModel("gemini-2.5-flash")

PROMPT = """다음 이력서 원문을 분석하여 JSON 형태로 추출하세요.

1. summary: 지원자의 직무 역량과 경력을 3~5문장으로 요약. 연락처(전화번호, 이메일), 주소, 생년월일은 절대 포함 금지.
2. current_company: 최근 직장명. 미상 금지. 유추할 것.
3. sector: 주요 활동 도메인을 1~2단어로 명확히 분류. 미분류 금지.

결과는 반드시 순수한 JSON 형식으로 작성하세요.
{"summary": "...", "current_company": "...", "sector": "..."}

[이력서 원문]
"""

def main():
    print("Restarting A Track - Linear Safe Parsing...")
    conn = sqlite3.connect("candidates.db", timeout=20)
    c = conn.cursor()
    c.execute("SELECT id, document_hash, name_kr, raw_text FROM candidates WHERE is_duplicate=0 AND is_parsed=0")
    targets = c.fetchall()
    
    total = len(targets)
    print(f"Target count: {total}")
    
    model = setup_gemini()
    
    cache_path = 'candidates_cache_jd.json'
    with open(cache_path, 'r', encoding='utf-8') as f:
        cache = json.load(f)
    cache_map = {str(item['id']).replace('-', ''): item for item in cache}
    
    success = 0
    fail = 0
    
    for i, r in enumerate(targets):
        cid, doc_hash, name, text = r
        try:
            if not text or len(text.strip()) < 50:
                print(f"Skipping empty text: {name}")
                continue
                
            res = model.generate_content(PROMPT + text[:15000])
            txt = res.text.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
            parsed = json.loads(txt)
            
            c.execute("UPDATE candidates SET is_parsed=1, updated_at=? WHERE document_hash=?", 
                        (datetime.now().isoformat(), doc_hash))
            
            cid_str = str(cid).replace('-', '')
            if cid_str in cache_map:
                cache_map[cid_str]['summary'] = parsed.get('summary', '')
                cache_map[cid_str]['profile_summary'] = parsed.get('summary', '')
                cache_map[cid_str]['current_company'] = parsed.get('current_company', '')
                cache_map[cid_str]['sector'] = parsed.get('sector', '')
            
            success += 1
        except Exception as e:
            fail += 1
            print(f"[{i+1}/{total}] Failed {name}")
            
        time.sleep(0.5) # Soft Gemini Rate limit
        
        if (i+1) % 20 == 0:
            print(f"Progress: {i+1}/{total} | Success: {success} | Fail: {fail}")
            conn.commit()
            with open(cache_path, 'w', encoding='utf-8') as f:
                json.dump(cache, f, ensure_ascii=False, indent=2)
                
    conn.commit()
    with open(cache_path, 'w', encoding='utf-8') as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)
    conn.close()
    print("Done parsing A track.")

if __name__ == "__main__":
    main()
