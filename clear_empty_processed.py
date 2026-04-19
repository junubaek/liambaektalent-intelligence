import json
import os

PROGRESS_FILE = r"C:\Users\cazam\Downloads\이력서자동분석검색시스템\processed.json"

try:
    with open(PROGRESS_FILE, "r", encoding="utf-8") as f:
        processed = json.load(f)
except Exception:
    processed = {}

old_count = len(processed)

keys_to_remove = []
for k, v in processed.items():
    if v.get("text_hash") == "":
        keys_to_remove.append(k)

for k in keys_to_remove:
    del processed[k]

new_count = len(processed)

with open(PROGRESS_FILE, "w", encoding="utf-8") as f:
    json.dump(processed, f, ensure_ascii=False, indent=2)

print(f"Removed {old_count - new_count} empty records from processed.json")
