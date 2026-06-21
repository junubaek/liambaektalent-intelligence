import os, sys
sys.stdout.reconfigure(encoding='utf-8')
resume_dir = r'C:\Users\cazam\Downloads\02_resume 전처리'
files = [f for f in os.listdir(resume_dir) if f.lower().endswith(('.pdf','.docx','.doc','.hwp','.txt'))]
from collections import Counter
exts = Counter(f.split('.')[-1].lower() for f in files)
print('확장자 분포:', dict(exts))
print('총 파일 수:', len(files))
import os.path
small = [f for f in files if os.path.getsize(os.path.join(resume_dir, f)) < 1000]
print(f'1KB 미만 (빈 파일 의심): {len(small)}개')
for f in small[:5]:
    print(f'  {f}')
