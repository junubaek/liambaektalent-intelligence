import sqlite3
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

conn = sqlite3.connect('candidates.db')
cursor = conn.cursor()

print("--- 1. Candidates Table Schema ---")
cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='candidates'")
schema = cursor.fetchone()
print(schema[0] if schema else "Table not found")

print("\n--- 2. Sample raw_text for DOB patterns ---")
cursor.execute("SELECT id, name_kr, raw_text FROM candidates WHERE raw_text IS NOT NULL LIMIT 10")
rows = cursor.fetchall()

for row in rows:
    cid, name, raw_text = row
    # Simple regex to find dates like 1980, 1990, 생년월일, 출생
    matches = re.finditer(r'(.{0,15})(생년월일|주민등록|출생|19\d{2}|200\d)(.{0,15})', raw_text)
    match_strings = [m.group(0).replace('\n', ' ') for m in matches]
    
    if match_strings:
        print(f"[{name}] Found patterns: {match_strings[:3]}") # Print up to 3 matches
    else:
        print(f"[{name}] No DOB patterns found.")

print("\nDone.")
