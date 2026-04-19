import sqlite3
import json
import fitz
import google.generativeai as genai

with open('secrets.json', 'r', encoding='utf-8') as f: secrets = json.load(f)
genai.configure(api_key=secrets.get('GEMINI_API_KEY', ''))
model_text = genai.GenerativeModel('gemini-2.5-flash-lite', generation_config={'response_mime_type': 'application/json'})
model_vision = genai.GenerativeModel('gemini-2.5-flash', generation_config={'response_mime_type': 'application/json'})

conn = sqlite3.connect(r'c:\Users\cazam\Downloads\이력서자동분석검색시스템\candidates.db')
c = conn.cursor()

def extract_careers_from_text(text):
    prompt = f"""아래 이력서 전문에서 직무(careers)를 추출하세요. 한진희의 경우 후반부 삼성전자, 하이닉스 내용을 반드시 포함하세요.
[JSON 포맷]
{{
  "representative_position": "문자열(최대 8글자 단어, 없으면 빈문자열)",
  "careers": [
    {{ "company": "회사명(미상)", "title": "직급/직무", "start_date": "YYYY-MM", "end_date": "YYYY-MM" }}
  ]
}}
[이력서 전문]
{text[:15000]}"""
    try:
        res = model_text.generate_content(prompt).text.strip()
        data = json.loads(res)
        car = json.dumps(data.get('careers', []), ensure_ascii=False)
        pos = data.get('representative_position', '')
        return car, pos
    except Exception as e:
        print("Text extraction error:", e)
        return None, None

def extract_careers_from_file_api(path):
    sample_file = genai.upload_file(path=path)
    prompt = """문서에서 직무(careers) 데이터를 다음과 같은 JSON 포맷으로 철저히 완전하게 OCR해서 추출하세요.
[JSON 포맷]
{
  "representative_position": "문자열(최대 8글자 단어)",
  "careers": [
    { "company": "회사명(미상)", "title": "직급/직무", "start_date": "YYYY-MM", "end_date": "YYYY-MM" }
  ]
}"""
    try:
        res = model_vision.generate_content([prompt, sample_file]).text.strip()
        data = json.loads(res)
        car = json.dumps(data.get('careers', []), ensure_ascii=False)
        pos = data.get('representative_position', '')
        return car, pos
    except Exception as e:
        print("Vision extraction error:", e)
        return None, None
    finally:
        try: genai.delete_file(sample_file.name)
        except: pass

tasks = [
    ("이소연(클라우드엔지니어)", r"C:\Users\cazam\Downloads\02_resume 전처리\[NC] 이소연(투자담당자)부문_90.pdf", False, "이소연(투자담당자)"),
    ("법무법인", r"C:\Users\cazam\Downloads\02_resume 전처리\[해시드스튜디오] 이재규(사내변호사)부문.pdf", False, "이재규(사내변호사)"),
    ("김진영(머신러닝)", r"C:\Users\cazam\Downloads\02_resume 전처리\[뷰노] 김진영(AI)부문.pdf", False, None),
    ("한진희", r"C:\Users\cazam\Downloads\02_resume 전처리\SK하이닉스_계측분석_한진희.pdf", False, None),
    ("이현재", r"C:\Users\cazam\Downloads\02_resume 전처리\[크몽]Java백엔드(주니어)-이현재.pdf", False, None),
    ("류한별", r"C:\Users\cazam\Downloads\02_resume 전처리\[네이버] 류한별(BE개발)부문.pdf", False, None),
    ("김율희", r"C:\Users\cazam\Downloads\02_resume 전처리\[챌린저스] 김율희(UX 디자이너)부문.pdf", True, None),
    ("이희진", r"C:\Users\cazam\Downloads\02_resume 전처리\[매드업] 이희진(CTO)부문.pdf", True, None),
    ("신혜수", r"C:\Users\cazam\Downloads\02_resume 전처리\[디셈버앤컴퍼니] 신혜수(사내변호사)부문.pdf", True, None)
]

for old_name, path, use_vision, name_override in tasks:
    print(f"Processing {old_name}...")
    car, pos = None, None
    raw_text = ""
    
    if not use_vision:
        try:
            doc = fitz.open(path)
            for page in doc: raw_text += page.get_text()
            car, pos = extract_careers_from_text(raw_text)
        except Exception as e:
            print("Error parsing PDF locally for", old_name, ":", e)
    else:
        car, pos = extract_careers_from_file_api(path)
        raw_text = "Image PDF successfully parsed via Gemini API"

    if car and len(car) > 5 and car != '[]':
        c.execute("SELECT id FROM candidates WHERE name_kr=?", (old_name,))
        rows = c.fetchall()
        if not rows:
            print(f"Could not find {old_name} in DB.")
            continue
        db_id = rows[0][0]
        
        final_name = old_name
        if name_override:
            final_name = name_override
        elif pos and '(' not in old_name:
            clean_pos = str(pos).replace('(', '').replace(')', '').strip()
            if clean_pos: final_name = f"{old_name}({clean_pos})"

        c.execute("UPDATE candidates SET raw_text=?, careers_json=?, name_kr=? WHERE id=?", (raw_text, car, final_name, db_id))
        conn.commit()
        print(f" -> Success! Updated as {final_name}")
    else:
        print(f" -> Failed to extract careers. car={car}")

conn.close()
