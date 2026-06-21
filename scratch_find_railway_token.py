import os
import sys

sys.stdout.reconfigure(encoding='utf-8')
root_dir = r"C:\Users\cazam\Downloads\이력서자동분석검색시스템"

print("Searching for tokens or railway credentials...")
extensions = ['.py', '.json', '.txt', '.ps1', '.bat', '.toml']
for root, dirs, files in os.walk(root_dir):
    if '.venv' in root or '.git' in root or '__pycache__' in root:
        continue
    for file in files:
        if any(file.endswith(ext) for ext in extensions):
            path = os.path.join(root, file)
            try:
                with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                if 'RAILWAY_TOKEN' in content or 'railway token' in content.lower():
                    print(f"Found in {path}")
                    for line in content.splitlines():
                        if 'TOKEN' in line or 'railway' in line.lower():
                            print("  ", line[:150])
            except Exception as e:
                pass
