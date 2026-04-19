import sqlite3
import re

db_path = "candidates.db"

def check():
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    
    # 1. Update known wrong names if raw_text contains Kang Min Sung, etc.
    rows = cur.execute("SELECT id, name_kr, raw_text FROM candidates WHERE name_kr IN ('자금', '재무회계', '[자금]', '[재무회계]')").fetchall()
    
    for row in rows:
        cid, name, raw_text = row
        print(f"Generic Name: {name} (ID: {cid})")
        if raw_text:
            m = re.search(r'강민성|이종구|김현구', raw_text)
            if m:
                print(f"  -> Found real name in text: {m.group(0)}")
        print("---")
        
    print("Done")
    
if __name__ == "__main__":
    check()
