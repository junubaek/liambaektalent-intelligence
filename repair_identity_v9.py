import sqlite3
import json
import re
import google.generativeai as genai
from tqdm import tqdm

with open("secrets.json", "r", encoding="utf-8") as f:
    secrets = json.load(f)
genai.configure(api_key=secrets.get("GEMINI_API_KEY", ""))
model = genai.GenerativeModel('gemini-2.5-flash-lite')

def get_real_name(text):
    if not text or len(text) < 50: return None
    prompt = f"다음 이력서 텍스트에서 후보자의 한글 본명(이름)만 정확하게 1단어로 출력하세요. 직급이나 인사말 등은 제외하세요.\n\n{text[:1000]}"
    try:
        res = model.generate_content(prompt).text.strip()
        name = re.sub(r'[^가-힣a-zA-Z]', '', res)
        if 2 <= len(name) <= 5: return name
    except:
        pass
    return None

conn = sqlite3.connect("candidates.db")
c = conn.cursor()

# 오염된 이름 목록
suspicious = ['김대용', '미상', 'JY', '삼정']

# 1. 텍스트가 의미있는(100자 이상) 행들 이름 추출
c.execute(f"SELECT id, name_kr, raw_text FROM candidates WHERE name_kr IN ({','.join(['?']*len(suspicious))})", suspicious)
rows = c.fetchall()

print(f"Total polluted rows to check: {len(rows)}")

updates = 0
for r_id, old_name, raw_text in tqdm(rows):
    if len(str(raw_text)) > 100:
        real_name = get_real_name(str(raw_text))
        if real_name and real_name != old_name:
            c.execute("UPDATE candidates SET name_kr = ? WHERE id = ?", (real_name, r_id))
            updates += 1
            if updates % 10 == 0:
                conn.commit()

conn.commit()

# 2. 정말 내용이 100자 미만이거나 파일명 뿐인 쓸모없는 가비지 행들은 삭제하여 DB 최적화
c.execute(f"DELETE FROM candidates WHERE name_kr IN ({','.join(['?']*len(suspicious))}) AND LENGTH(CAST(raw_text AS TEXT)) < 100", suspicious)
deleted = c.rowcount

conn.commit()
conn.close()

print(f"Fixed Names: {updates} rows.")
print(f"Deleted Garbage Rows: {deleted} rows.")
