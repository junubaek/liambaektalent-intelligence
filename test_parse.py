import sys, os
sys.path.append(os.path.abspath('.'))
from dynamic_parser import extract_text, parse_resume

folder = r'C:\Users\cazam\Downloads\02_resume 전처리'
files = os.listdir(folder)
target = [f for f in files if '박성준' in f]
print('찾은 파일:', target)
if target:
    text = extract_text(os.path.join(folder, target[0]))
    print('텍스트 길이:', len(text))
    print('텍스트 앞부분:', text[:300])
    result = parse_resume(text)
    print('파싱 결과:', result)
