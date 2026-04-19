import sqlite3
import json
import sys
sys.stdout.reconfigure(encoding='utf-8')
con = sqlite3.connect('candidates.db')
c = con.cursor()
c.execute("SELECT parsed_json FROM parsing_cache LIMIT 1")
row = c.fetchone()
parsed = json.loads(row[0])
print(json.dumps(parsed, indent=2, ensure_ascii=False))
