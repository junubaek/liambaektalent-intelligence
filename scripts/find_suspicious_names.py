import json
import sqlite3

def find_suspicious():
    conn = sqlite3.connect('candidates.db')
    c = conn.cursor()
    c.execute("SELECT id, name_kr FROM candidates")
    rows = c.fetchall()

    suspicious = []
    for cid, name in rows:
        if not name:
            suspicious.append((cid, "EMPTY"))
            continue
            
        clean = name.replace(' ', '')
        
        # Checking for common non-name keywords
        bad_words = ['경력', '이력', '개발자', '엔지니어', '매니저', '포트폴리오', 'resume', 'profile', '지원', '본부', '서버', '기술']
        
        is_suspicious = False
        
        if any(w in clean.lower() for w in bad_words):
            is_suspicious = True
        elif len(clean) > 4 or len(clean) < 2:
            is_suspicious = True
            
        if is_suspicious:
            suspicious.append((cid, name))

    print(f"Total Suspicious: {len(suspicious)}")
    for i, (cid, name) in enumerate(suspicious[:50]):
        print(f"{i}: {name}")

if __name__ == "__main__":
    find_suspicious()
