import sqlite3
import json
import time
import os
import traceback
import google.generativeai as genai

def recover_all():
    if not os.path.exists('secrets.json'): return
    with open('secrets.json', 'r', encoding='utf-8') as f:
        secrets = json.load(f)
    genai.configure(api_key=secrets.get('GEMINI_API_KEY'))
    model = genai.GenerativeModel('gemini-2.5-flash')
    
    conn = sqlite3.connect('candidates.db')
    c = conn.cursor()
    # Get everyone missing email OR missing education
    c.execute("SELECT id, raw_text, name_kr FROM candidates WHERE email IS NULL OR email = '' OR education_json IS NULL OR education_json = '[]' OR education_json = ''")
    rows = c.fetchall()
    
    print(f"Starting Background Mass Recovery Tool. Total Targets: {len(rows)}")
    
    with open('candidates_cache_jd.json', 'r', encoding='utf-8') as f:
        cache = json.load(f)
    cache_map = {str(item['id']).replace('-', ''): item for item in cache}
    
    for idx, row in enumerate(rows):
        cid, raw, name = row
        if not raw or len(raw) < 50: continue
        
        cid_clean = str(cid).replace('-', '')
        
        prompt = f"""
        다음 이력서 원문에서 연락처, 이메일, 최종학력 기재사항을 극도로 정확하게 추출해 JSON으로 반환해.
        원문: {raw[:3000]}
        필수 응답포맷(JSON Only):
        {{
            "email": "이메일 또는 빈문자열",
            "phone": "전화번호 또는 빈문자열",
            "education": [{{"school": "대학교이름", "major": "전공", "degree": "학사/석사/박사", "graduation_year": "YYYY"}}]
        }}
        """
        try:
            res = model.generate_content(prompt)
            data = res.text.replace('```json', '').replace('```', '').strip()
            parsed = json.loads(data)
            
            email = parsed.get('email', '')
            phone = parsed.get('phone', '')
            edu = json.dumps(parsed.get('education', []), ensure_ascii=False)
            
            c.execute("UPDATE candidates SET email = ?, phone = ?, education_json = ? WHERE id = ?", (email, phone, edu, cid))
            conn.commit()
            
            # Update cache as well
            if cid_clean in cache_map:
                cache_map[cid_clean]['email'] = email
                cache_map[cid_clean]['phone'] = phone
                
            print(f"[{idx+1}/{len(rows)}] ({name}) -> Email: {email}, Edu: {len(parsed.get('education', []))}")
            time.sleep(2) # rate limit
            
        except Exception as e:
            print(f"[{idx+1}/{len(rows)}] Error on {name}")

    with open('candidates_cache_jd.json', 'w', encoding='utf-8') as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)
        
    print("Background Parsing Finished.")

if __name__ == "__main__":
    recover_all()
