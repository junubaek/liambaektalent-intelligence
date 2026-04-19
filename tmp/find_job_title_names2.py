import sqlite3

conn = sqlite3.connect('candidates.db')
cursor = conn.cursor()

# Get column names
cursor.execute("SELECT * FROM candidates LIMIT 1")
columns = [description[0] for description in cursor.description]

print("Columns:", columns)

# Now query
cursor.execute("SELECT name_kr, document_hash FROM candidates")
rows = cursor.fetchall()

suspects = []
job_keywords = ["자금", "재무", "회계", "HR", "인사", "마케팅", "영업", "Sales", "기획", 
               "개발", "디자인", "MD", "상품", "전략", "PR", "총무", "품질", "오퍼레이션", "경영"]
               
for name_kr, doc_hash in rows:
    if not name_kr:
        continue
        
    is_suspect = False
    
    for word in job_keywords:
        # Avoid matching common name characters if they just happen to contain e.g. "기", "영" etc
        # Usually these are full names, so if it exactly matches or is extremely short + keyword
        if word in name_kr and len(name_kr) <= 6 and not name_kr.endswith("님") and name_kr not in ["권기획", "이경영", "김경영", "박영업", "최디자인", "이영업"]:
            # Actually just look for EXACT match or very clear job titles
            if name_kr == word or name_kr == f"{word}담당" or name_kr == f"{word}팀장" or "전문가" in name_kr:
                is_suspect = True
            elif len(name_kr) < 5 and word in name_kr:
                # e.g., "재무회계", "마케팅", "자금"
                is_suspect = True
    
    if is_suspect:
        suspects.append({"name": name_kr, "hash": doc_hash})

print(f"\nTotal suspects found: {len(suspects)}")
for s in suspects:
    print(f"Name: {s['name']:<10} | Hash: {s['hash']}")

conn.close()
