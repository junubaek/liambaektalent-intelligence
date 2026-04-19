import sqlite3
import os

print("--- Checking SQLite DB ---")
try:
    conn = sqlite3.connect('candidates.db')
    cursor = conn.cursor()

    cursor.execute("""
      SELECT id, name_kr, document_hash, 
             length(raw_text) as text_len
      FROM candidates
      WHERE name_kr LIKE '%강민성%'
         OR name_kr LIKE '%이종구%'
         OR name_kr LIKE '%김현구%'
    """)
    db_results = cursor.fetchall()
    print("DB Results:", db_results)
except Exception as e:
    print("DB Error:", e)

print("\n--- Checking Local Folder ---")
folder = r'C:\Users\cazam\Downloads\02_resume_converted_v8'
try:
    files = os.listdir(folder)
    matches = [f for f in files if '강민성' in f or '이종구' in f or '김현구' in f]
    print("Folder Matches:", matches)
except Exception as e:
    print("Folder Error:", e)

print("\nDone")
