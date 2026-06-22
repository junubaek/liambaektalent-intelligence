import sys, codecs
sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer)
content = open('incremental_ingest_v11.py', encoding='utf-8', errors='replace').read()
lines = content.split('\n')
for i, line in enumerate(lines[258:310], start=258):
    print(i, line)
