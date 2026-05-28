import sqlite3
import json

conn = sqlite3.connect('candidates.db')
cur = conn.cursor()

# Query specific candidate and see its parsing_cache connection
cur.execute('''
    SELECT c.id, c.name_kr, c.sector, c.profile_summary, c.current_company
    FROM candidates c
    WHERE c.name_kr IN ('김국현','우형일','황의영') AND c.is_duplicate=0
''')
for cid, name, sector, summary, company in cur.fetchall():
    print(f"\nCandidate [{name}]: sector={sector}, company={company}")
    print(f"  summary={summary[:100] if summary else None}")
    
    cur.execute("SELECT parsed_json FROM parsing_cache WHERE candidate_id=?", (cid,))
    prow = cur.fetchone()
    if prow:
        try:
            pdict = json.loads(prow[0])
            print("  ParsingCache profile_summary:", pdict.get('profile_summary'))
            print("  ParsingCache main_sectors:", pdict.get('main_sectors'))
            print("  ParsingCache current_company:", pdict.get('current_company'))
        except Exception as ex:
            print("  Error decoding json:", ex)
    else:
        print("  No parsing_cache row found for candidate_id")
            
conn.close()
