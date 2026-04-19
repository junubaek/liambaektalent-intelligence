import sqlite3
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

# Search for original extensions
folders = [
    r"C:\Users\cazam\Downloads\02_resume 전처리",
    r"C:\Users\cazam\Downloads\02_resume_converted_docx",
    r"C:\Users\cazam\Downloads\02_resume_converted_v8"
]

def find_file(name):
    for folder in folders:
        if not os.path.exists(folder):
            continue
        for f in os.listdir(folder):
            if name in f:
                return f, folder
    return None, None

def inspect():
    db = sqlite3.connect('candidates.db')
    c = db.cursor()
    
    names = ['채봉수', '이정선']
    
    for name in names:
        print(f"\n[{name}] 검사 ----------------------------------")
        
        # 1 & 2. DB raw_text 확인
        c.execute("SELECT raw_text FROM candidates WHERE name_kr=?", (name,))
        rows = c.fetchall()
        if not rows:
            print("DB에 존재하지 않습니다.")
            continue
            
        raw_text = rows[0][0]
        if raw_text:
            print(f"- DB Text Length: {len(raw_text)}")
            print(f"- 프롬프트에 제공된 시작 500자:\n{raw_text[:500]}")
        else:
            print("- DB raw_text: NULL 입니다.")
            
        # 3. 원본 물리 파일 확인
        filename, folder = find_file(name)
        if filename:
            print(f"- 원본 파일: {filename}")
            print(f"- 위치: {folder}")
            print(f"- 확장자: {filename.split('.')[-1]}")
        else:
            print("- 원본 물리 파일을 찾을 수 없습니다.")

if __name__ == "__main__":
    inspect()
