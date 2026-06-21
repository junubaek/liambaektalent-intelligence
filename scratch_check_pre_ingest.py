import os
import sqlite3
import sys

sys.stdout.reconfigure(encoding='utf-8')

folder = r'C:\Users\cazam\Downloads\02_resume 전처리'
if not os.path.exists(folder):
    print(f"오류: 폴더가 존재하지 않습니다. ({folder})")
    sys.exit(1)

files = [f for f in os.listdir(folder) if f.endswith(('.pdf','.docx','.doc'))]
print(f'폴더 내 파일 수: {len(files)}')

conn = sqlite3.connect('candidates.db')
cur = conn.cursor()
cur.execute('SELECT COUNT(*) FROM candidates WHERE is_duplicate=0')
print(f'현재 활성 후보자: {cur.fetchone()[0]}명')

# 이미 파싱된 파일명 기반 체크
cur.execute('SELECT source_file FROM candidates WHERE source_file IS NOT NULL')
parsed = {r[0] for r in cur.fetchall()}
print(f'source_file 등록된 레코드: {len(parsed)}개')

new_files = [f for f in files if f not in parsed]
print(f'신규 파싱 대상: {len(new_files)}개')
conn.close()
