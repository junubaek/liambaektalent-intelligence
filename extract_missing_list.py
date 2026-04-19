import sqlite3
import os

db = sqlite3.connect('candidates.db')
res = db.execute('''
    SELECT name_kr, id 
    FROM candidates 
    WHERE is_duplicate=0 
    AND (google_drive_url IS NULL OR google_drive_url="" OR google_drive_url="#")
''').fetchall()

doc = "# 📄 잔여 누락 236명 명단\n\n"
doc += "현재 구글 드라이브(혹은 Docs/Sheets) URL을 찾을 수 없거나 노션 페이지 내에 이력서 파일 블록이 없는 236명의 명단입니다. (주로 404 접근 거부 혹은 텍스트/표로 직접 기재된 이력서입니다.)\n\n"
doc += "| 연번 | 후보자 이름 | Notion ID (ID) |\n"
doc += "|:---:|:---|:---|\n"

for i, r in enumerate(res):
    name = r[0] if r[0] else "이름 없음"
    doc += f"| {i+1} | {name} | `{r[1]}` |\n"

with open(r'C:\Users\cazam\.gemini\antigravity\brain\40516708-d2c8-4e50-a5f8-ff10183de737\artifacts\missing_236_list.md', 'w', encoding='utf-8') as f:
    f.write(doc)
    
print("Artifact generated.")
