import sqlite3
from collections import Counter

conn = sqlite3.connect('candidates.db')
cursor = conn.cursor()

cursor.execute("SELECT name_kr FROM candidates")
rows = cursor.fetchall()

job_keywords = ["자금", "재무", "회계", "HR", "인사", "마케팅", "영업", "Sales", "기획", 
               "개발", "디자인", "MD", "상품", "전략", "PR", "총무", "품질", "오퍼레이션", "경영"]

bad_names = []

for row in rows:
    name_kr = row[0]
    if not name_kr:
        continue
        
    is_suspect = False
    
    for word in job_keywords:
        if word in name_kr and len(name_kr) <= 6 and not name_kr.endswith("님") and name_kr not in ["권기획", "이경영", "김경영", "박영업", "최디자인", "이영업"]:
            if name_kr == word or name_kr == f"{word}담당" or name_kr == f"{word}팀장" or "전문가" in name_kr:
                is_suspect = True
            elif len(name_kr) < 5 and word in name_kr:
                is_suspect = True
                
    if is_suspect:
        bad_names.append(name_kr)

counts = Counter(bad_names)

print(f"\n=== 직무명(포지션명)으로 잘못 파싱된 이름 목록 (총 {sum(counts.values())}건) ===")
for name, cnt in counts.most_common():
    print(f"- {name}: {cnt}명")

conn.close()
