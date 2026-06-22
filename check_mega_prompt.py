import sys, codecs
sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer)
content = open('incremental_ingest_v11.py', encoding='utf-8', errors='replace').read()
idx = content.find('MEGA_PROMPT')
print(content[idx:idx+3000])
