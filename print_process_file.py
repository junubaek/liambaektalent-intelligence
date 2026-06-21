import sys, pathlib
sys.stdout.reconfigure(encoding='utf-8')
path = pathlib.Path('incremental_ingest_v10.py')
lines = path.read_text(encoding='utf-8').split('\n')
start, end = 226, 416  # 0-indexed line numbers for slice
for i in range(start, min(end, len(lines))):
    print(lines[i])
