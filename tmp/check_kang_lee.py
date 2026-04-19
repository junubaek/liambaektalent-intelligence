import os
import sqlite3
import sys

sys.stdout.reconfigure(encoding='utf-8')

print("--- 1. Check converted_v8 folder ---")
idx_folder = r'C:\Users\cazam\Downloads\02_resume_converted_v8'
try:
    if os.path.exists(idx_folder):
        matches = [f for f in os.listdir(idx_folder) if '강민성' in f or '이종구' in f]
        print(f"Matches in converted_v8: {matches}")
    else:
        print("converted_v8 folder not found.")
except Exception as e:
    print(f"Error checking folder: {e}")

print("\n--- 2. Check DB for misnamed candidates ---")
try:
    conn = sqlite3.connect('candidates.db')
    cursor = conn.cursor()
    cursor.execute("""
      SELECT name_kr, document_hash, length(raw_text) as text_len, raw_text
      FROM candidates
      WHERE name_kr LIKE '%재무회계%'
         OR name_kr LIKE '%Finance%'
         OR name_kr LIKE '%클레온%'
    """)
    rows = cursor.fetchall()
    
    found_kang = False
    found_lee = False
    kang_hash = None
    lee_hash = None
    
    for r in rows:
        name_kr, doc_hash, text_len, raw_text = r
        raw_safe = raw_text[:200] if raw_text else ""
        print(f"DB Record -> name_kr: {name_kr}, doc_hash: {doc_hash}, len: {text_len}")
        if raw_text and '강민성' in raw_text:
            print("  --> [Match] '강민성' found in raw_text!")
            kang_hash = doc_hash
            found_kang = True
        if raw_text and '이종구' in raw_text:
            print("  --> [Match] '이종구' found in raw_text!")
            lee_hash = doc_hash
            found_lee = True

    print("\n--- Summary ---")
    if found_kang:
        print(f"Kang Min-sung found with hash {kang_hash}")
    if found_lee:
        print(f"Lee Jong-gu found with hash {lee_hash}")

except Exception as e:
    print(f"Error checking DB: {e}")
