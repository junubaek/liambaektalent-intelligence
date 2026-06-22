import sys, codecs
sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer)
content = open('main.py', encoding='utf-8', errors='replace').read()
idx = content.find('bm25')
if idx < 0:
    idx = content.find('BM25')
print(content[max(0,idx-100):idx+300])
