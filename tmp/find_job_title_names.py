import sqlite3
import re

try:
    conn = sqlite3.connect('candidates.db')
    cursor = conn.cursor()
    cursor.execute("""
        SELECT document_hash, filename, name_kr, email, phone
        FROM candidates
    """)
    rows = cursor.fetchall()

    suspects = []
    
    # Common job titles or departments
    job_keywords = ["자금", "재무", "회계", "HR", "인사", "마케팅", "영업", "Sales", "기획", 
                   "개발", "디자인", "MD", "상품", "전략", "PR", "총무", "품질", "오퍼레이션", "경영"]
                   
    for doc_hash, filename, name_kr, email, phone in rows:
        if not name_kr:
            continue
            
        is_suspect = False
        
        # Condition 1: Contains job keyword
        for word in job_keywords:
            if word in name_kr:
                is_suspect = True
                break
                
        # Condition 2: name is 2 chars and first char is not a common surname, or just looks weird like "자금"
        if name_kr == "자금" or name_kr == "재무회계":
            is_suspect = True
            
        if is_suspect:
            suspects.append({"name": name_kr, "file": filename, "hash": doc_hash})

    # Sort suspects and just print unique suspicious names and their files
    print(f"Total suspects found: {len(suspects)}")
    for s in suspects[:50]:  # print up to 50
        print(f"Name: {s['name']:<10} | File: {s['file']}")

except Exception as e:
    print(f"Error: {e}")
finally:
    if 'conn' in locals():
        conn.close()
