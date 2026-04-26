import sqlite3
import json

db_path = 'candidates.db'
conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
cur = conn.cursor()

cur.execute("SELECT * FROM candidates WHERE id = '32022567-1b6f-81cf-af18-cbdada2eecf0'")
row = cur.fetchone()
if row:
    d = dict(row)
    print('ID:', d['id'])
    print('Name_KR:', d['name_kr'].encode('utf-8', 'ignore').decode('utf-8'))
    
    # Try parsing the Notion URL from notions column if it exists
    notion_url = d.get('notion_url', 'N/A')
    print('Notion URL:', notion_url)
    
    # Try finding any other name traces in the raw text
    parsed_json = d.get('parsed_json', '{}')
    try:
        pj = json.loads(parsed_json)
        print('Parsed Name_kr:', pj.get('name_kr'))
        print('Parsed Name:', pj.get('name'))
        print('Parsed Email:', pj.get('email'))
        print('Parsed Phone:', pj.get('phone'))
    except Exception:
        pass
else:
    print('Not found in SQLite.')

conn.close()
