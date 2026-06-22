import sys, codecs
sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer)
content = open('incremental_ingest_v11.py', encoding='utf-8', errors='replace').read()
lines = content.split('\n')

# GPT 호출 부분 찾기
for i, line in enumerate(lines):
    if 'chat.completions' in line or 'system' in line.lower() and 'skill' in line.lower():
        start = max(0, i-5)
        end = min(len(lines), i+30)
        print(f'--- Found at line {i} ---')
        for j, l in enumerate(lines[start:end], start=start):
            print(j, l)
        print()
        break
