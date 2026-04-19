import sqlite3
import json
import time
import os
import google.generativeai as genai
from tqdm import tqdm

# Load API key
with open('secrets.json', 'r') as f:
    secret_data = json.load(f)
gemini_api_key = secret_data.get('GEMINI_API_KEY')

if not gemini_api_key:
    print('Failed to load GEMINI_API_KEY from secrets.json')
    exit(1)

genai.configure(api_key=gemini_api_key)
model = genai.GenerativeModel(
    'gemini-2.5-flash',
    generation_config={"response_mime_type": "application/json"}
)

DB_PATH = "candidates.db"

EXTRACTION_PROMPT = """
당신은 전문 헤드헌터 데이터 파서입니다. 
주어진 이력서 원문을 분석하여 다음 JSON 스키마에 맞게 데이터를 추출하세요.
정보가 없거나 모호한 경우 절대 지어내지 말고 null 또는 빈 배열[]을 반환하세요.

[JSON 스키마]
{
  "birth_year": 정수형 (예: 1985, 없으면 null. '85년생'이나 주민번호 앞자리 등으로 유추 가능하면 4자리 연도로 변환),
  "education": [
    {
      "school": "학교명",
      "major": "전공",
      "degree": "학위 (예: 학사, 석사, 박사, 없으면 null)",
      "graduation_year": "졸업연도 (예: 2010, 없으면 null)"
    }
  ],
  "careers": [
    {
      "company": "회사명",
      "title": "직급/직무",
      "start_date": "입사 (YYYY-MM 형식, 모르면 YYYY)",
      "end_date": "퇴사 (YYYY-MM 형식, 재직중이면 '현재')"
    }
  ]
}

[이력서 원문]
{raw_text}
"""

def setup_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try: cursor.execute("ALTER TABLE candidates ADD COLUMN birth_year INTEGER")
    except: pass
    try: cursor.execute("ALTER TABLE candidates ADD COLUMN education_json TEXT")
    except: pass
    try: cursor.execute("ALTER TABLE candidates ADD COLUMN careers_json TEXT")
    except: pass
    conn.commit()
    conn.close()

def run_batch_patcher():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, raw_text FROM candidates 
        WHERE birth_year IS NULL OR education_json IS NULL
    """)
    targets = cursor.fetchall()
    
    print(f"🎯 총 {len(targets)}명의 이력서 백필 파싱 시작...")
    success_count = 0
    
    for candidate_id, raw_text in tqdm(targets):
        if not raw_text or len(raw_text) < 50:
            continue
            
        prompt = EXTRACTION_PROMPT.replace('{raw_text}', raw_text[:8000])
        
        try:
            response = model.generate_content(prompt)
            result = json.loads(response.text)
            
            birth_year = result.get('birth_year')
            education_json = json.dumps(result.get('education', []), ensure_ascii=False)
            careers_json = json.dumps(result.get('careers', []), ensure_ascii=False)
            
            cursor.execute("""
                UPDATE candidates 
                SET birth_year = ?, education_json = ?, careers_json = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (birth_year, education_json, careers_json, candidate_id))
            
            success_count += 1
            if success_count % 50 == 0:
                conn.commit()
                
            time.sleep(1.5) 
            
        except Exception as e:
            print(f"⚠️ ID {candidate_id} 파싱 실패: {e}")
            continue
            
    conn.commit()
    conn.close()
    print(f"✅ 백필 완료! (성공: {success_count}명)")

if __name__ == "__main__":
    setup_db()
    run_batch_patcher()
