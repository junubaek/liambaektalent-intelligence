import os
import sqlite3
import json

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(ROOT_DIR, "candidates.db")

bad_names = [
    '넵튠', '고위드', '전자', '협력팀', '뤼이드', '칼텍스', '엔카', 
    '기아', '긴트', '빙봉빙봉', '이케아', '요기요', '왓차'
]

conn = sqlite3.connect(DB_PATH)
c = conn.cursor()

results = []
for bn in bad_names:
    res = c.execute("SELECT id, name_kr, raw_text FROM candidates WHERE name_kr LIKE ?", (f'%{bn}%',)).fetchall()
    for row in res:
        cid = row[0]
        n_kr = row[1]
        text = str(row[2])[:50].split()
        first_word = text[0] if text else "None"
        second_word = text[1] if len(text) > 1 else "None"
        print(f"[{n_kr}] ID: {cid} / Text Start: {first_word} {second_word}")

print("\n--- Summary for Shin Mi Kyung ---")
res = c.execute("SELECT id, name_kr, raw_text FROM candidates WHERE name_kr LIKE '%심미경%'").fetchall()
for row in res:
    print(row[1], row[0])
