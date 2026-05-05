import sqlite3
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

def check_db():
    conn = sqlite3.connect('candidates.db')
    cur = conn.cursor()
    cur.execute("SELECT id, name_kr, current_company, careers_json, raw_text FROM candidates WHERE name_kr LIKE '%김은형%'")
    rows = cur.fetchall()
    
    for row in rows:
        cid, name, comp, careers_str, raw_text = row
        print(f"=== ID: {cid} | Name: {name} | Current: {comp} ===")
        if careers_str:
            try:
                careers = json.loads(careers_str)
                print("Careers:")
                for c in careers:
                    print(f"  - {c.get('company')} | {c.get('start_date')} ~ {c.get('end_date')} | {c.get('role')}")
            except Exception as e:
                print(f"Careers: Error parsing JSON - {e}")
        else:
            print("Careers: None")
            
        if raw_text:
            print(f"Raw Text Snippet (first 1000 chars):")
            # Replace problematic characters or just print a safe representation
            safe_text = raw_text[:1000].encode('utf-8', 'ignore').decode('utf-8')
            print(safe_text.replace('\n', '  '))
        print("\n")
        
    conn.close()

if __name__ == '__main__':
    check_db()
