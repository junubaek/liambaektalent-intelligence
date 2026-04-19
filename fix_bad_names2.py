import sqlite3
import json
import google.generativeai as genai

with open('secrets.json', 'r', encoding='utf-8') as f: secrets = json.load(f)
genai.configure(api_key=secrets.get('GEMINI_API_KEY', ''))
model = genai.GenerativeModel('gemini-2.5-flash-lite', generation_config={'response_mime_type': 'application/json'})

conn = sqlite3.connect(r'c:\Users\cazam\Downloads\이력서자동분석검색시스템\candidates.db')
c = conn.cursor()

names_to_fix = [
    'Curriculum Vitae -- John YH Lee', '_Jaehyun Jaden Lim 2020', 'Chan Woo Park', 'PM_Sanghyun Kim', 'Jin-Hyeok Lee',
    '웹젠', '이사만루', '채용팀장', 'WMS개발(Java개발자)', '전자정부프레임워크', '디자이너', 'WMS 개발(MES 개발)', 
    'WMS 개발(ERP 회계)', 'WMS개발(ERP개발)', '해당정보없음', 'WMS개발(MES전문가)'
]

q = ','.join(['?']*len(names_to_fix))
c.execute(f"SELECT id, name_kr, CAST(raw_text AS TEXT) FROM candidates WHERE name_kr IN ({q})", names_to_fix)

for db_id, old_name, text in c.fetchall():
    prompt = f"""이력서 전문 텍스트에서 지원자의 '실제 본명'(이름)만 정확하게 추출하세요. 영문 이름도 허용됩니다. 이력서 상단에 있습니다.
[JSON 형식]
{{ "real_name": "홍길동" }}
[이력서 텍스트]
{str(text)[:4000]}"""

    try:
        data = json.loads(model.generate_content(prompt).text.strip())
        real_name = data.get('real_name')
        if real_name: real_name = str(real_name).strip()
        
        if real_name and real_name != '미상' and len(real_name) <= 20:
            tag = ''
            if '(' in old_name:
                tag = old_name.split('(')[-1].replace(')', '').strip()
            new_name = real_name
            if tag and tag not in new_name:
                new_name = f'{real_name}({tag})'
            print(f'{old_name} => {new_name}')
            c.execute('UPDATE candidates SET name_kr=? WHERE id=?', (new_name, db_id))
        else:
            print(f'{old_name} => FAILED (found: {real_name})')
    except Exception as e:
        print(f'{old_name} => ERROR')

conn.commit()
conn.close()
