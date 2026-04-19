import sys

with open('step4_out.txt', 'r', encoding='utf-16le') as f:
    text = f.read()
    sys.stdout.buffer.write(text.encode('utf-8'))
