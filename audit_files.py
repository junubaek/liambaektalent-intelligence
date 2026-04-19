import os
import sqlite3

folders = [
    r'C:\Users\cazam\Downloads\02_resume 전처리',
    r'C:\Users\cazam\Downloads\02_resume_converted_v8'
]

for folder in folders:
    if not os.path.exists(folder):
        print(f'폴더 없음: {folder}')
        continue
    
    files = os.listdir(folder)
    sizes = []
    for f in files:
        fp = os.path.join(folder, f)
        if os.path.isfile(fp):
            sizes.append((f, os.path.getsize(fp)))
    
    print(f'\n=== {folder} ===')
    print(f'총 파일: {len(sizes)}개')
    print(f'10KB 미만: {sum(1 for _, s in sizes if s < 10000)}개')
    print(f'1KB 미만: {sum(1 for _, s in sizes if s < 1000)}개')
    
    # 작은 파일 10개
    small = sorted(sizes, key=lambda x: x[1])[:10]
    print('가장 작은 파일 10개:')
    for fname, fsize in small:
        print(f'  {fname}: {fsize:,}bytes')

print('\n=== raw_text 50자 미만인 381명 중 가장 길이 짧은 10명 샘플 ===')
db_path = r'C:\Users\cazam\Downloads\이력서자동분석검색시스템\candidates.db'
if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('''
        SELECT name_kr, length(raw_text) as len, raw_text
        FROM candidates
        WHERE length(raw_text) < 50
        ORDER BY len ASC
        LIMIT 10
    ''')
    for row in cursor.fetchall():
        print(f"{row['name_kr']} ({row['len']}자): {row['raw_text']}")
else:
    print('DB 파일을 찾을 수 없습니다.')
