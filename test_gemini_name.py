import sqlite3
import json
from google import genai
import time

def run_test():
    with open("secrets.json", "r", encoding="utf-8") as f:
        secrets = json.load(f)
        
    client = genai.Client(api_key=secrets["GEMINI_API_KEY"])
    
    conn = sqlite3.connect('candidates.db')
    cur = conn.cursor()
    
    # We will pick 10 rows where name is "김대용"
    cur.execute("SELECT id, document_hash, raw_text FROM candidates WHERE name_kr IN ('김대용') LIMIT 10")
    rows = cur.fetchall()
    
    print("=== 테스트 이름 추출 결과 (10건) ===")
    for row in rows:
        _id, doc_hash, raw_text = row
        if not raw_text: raw_text = ""
        
        prefix = raw_text[:300]
        prompt = f"""다음은 한국어 이력서 본문의 앞부분입니다.
지원자의 실제 이름(한국어 2-4글자)만 추출해주세요.
이름을 찾을 수 없으면 "미확인"이라고만 답하세요.
다른 설명 없이 이름만 답하세요.

이력서:
{prefix}
"""
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=prompt,
                )
                
                name = response.text.strip()
                if "미확인" in name:
                    name = "미확인"
                
                print(f"Hash: {doc_hash[:8]:<8} | 추출된 이름: {name}")
                break
            except Exception as e:
                if attempt == max_retries - 1:
                    print(f"Hash: {doc_hash[:8]:<8} | 실패: {e}")
                time.sleep(2)
                
    conn.close()

if __name__ == "__main__":
    run_test()
