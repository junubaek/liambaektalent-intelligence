import re

with open('backend/main.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Find all @app decorators and their function bodies
matches = re.finditer(r'@app\.[a-z_]+\("[^"]+"\)[^@]+', content)
for m in matches:
    block = m.group(0)
    lines = block.split('\n')
    print("ROUTE:", lines[0])
    for line in lines[1:8]:
        print("  ", line)
    print("...")
