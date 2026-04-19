import os
import sys
# force utf-8 encoding for stdout
sys.stdout.reconfigure(encoding='utf-8')

print("--- Checking 02_resume 전처리 Folder ---")
p = r'C:\Users\cazam\Downloads\02_resume 전처리'

if not os.path.exists(p):
    print(f"Folder not found: {p}")
else:
    files = os.listdir(p)
    matches = [f for f in files if '강민성' in f or '이종구' in f or '김현구' in f]
    print(f"Total files in folder: {len(files)}")
    print("Matches:")
    for m in matches:
        print(f" - {m}")
        
    print("Done checking.")
