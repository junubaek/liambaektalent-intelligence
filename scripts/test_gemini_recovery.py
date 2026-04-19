import sqlite3
import json
import time
import os
import google.generativeai as genai

def recover():
    if not os.path.exists('secrets.json'): return
    with open('secrets.json', 'r', encoding='utf-8') as f:
        secrets = json.load(f)
    genai.configure(api_key=secrets.get('GEMINI_API_KEY'))
    model = genai.GenerativeModel('gemini-1.5-pro-latest')
    
    conn = sqlite3.connect('candidates.db')
    c = conn.cursor()
    c.execute("SELECT id, raw_text, name_kr FROM candidates WHERE email IS NULL OR phone IS NULL OR email = '' OR phone = '' LIMIT 10")
    rows = c.fetchall()
    
    print(f"Testing recovery on {len(rows)} samples...")
    for row in rows:
        cid, raw, name = row
        if not raw or len(raw) < 50: continue
        
        prompt = f"""
        다음 이력서 원문에서 연락처, 이메일, 최종학력, 전체 경력 상세내역을 추출해 JSON으로 반환해.
        원문: {raw[:3000]}
        응답포맷: {{"email": "...", "phone": "...", "education": ["대학교 전공 학사"], "career_details": ["회사명 - 직무 기간"]}}
        """
        try:
            res = model.generate_content(prompt)
            print(f"[{name}] Result:")
            print(res.text[:150])
            time.sleep(2)
        except Exception as e:
            print(e)
            
if __name__ == "__main__":
    recover()
