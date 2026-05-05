import sqlite3
import re
import sys
sys.stdout.reconfigure(encoding='utf-8')

def extract_company(text):
    if not text: return None
    # Simple regex for common company patterns in resumes
    # e.g., "소속: XXX", "경력: YYY", "XXX (2020 - 2022)"
    patterns = [
        r"소속[:\s]+([^\n]+)",
        r"현재[:\s]+([^\n]+)",
        r"Company[:\s]+([^\n]+)",
        r"([가-힣\w\s\(\)]+)\s?[\(]?20\d{2}"
    ]
    for p in patterns:
        m = re.search(p, text)
        if m:
            return m.group(1).strip()
    return None

conn = sqlite3.connect('candidates.db')
cur = conn.cursor()

targets = ['정소윤', '조예원', '남현승', '김광우']

for name in targets:
    print(f"Analyzing {name}...")
    cur.execute("SELECT id, raw_text, current_company FROM candidates WHERE name_kr = ?", (name,))
    rows = cur.fetchall()
    for cid, text, curr in rows:
        print(f"  Current: {curr}")
        if not curr or curr == 'None' or curr == '미상':
            comp = extract_company(text)
            if comp:
                print(f"  Extracted: {comp}")
            else:
                # Try first 200 chars
                print(f"  Snippet: {text[:200] if text else 'No Text'}")

conn.close()
