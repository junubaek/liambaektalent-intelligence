import sys, pathlib
sys.stdout.reconfigure(encoding='utf-8')
script_path = pathlib.Path('incremental_ingest_v10.py')
text = script_path.read_text(encoding='utf-8')
lines = text.split('\n')
print('총 라인:', len(lines))
for i, line in enumerate(lines, 1):
    s = line.strip()
    if s.startswith('def ') or s.startswith('class '):
        print(i, s)
