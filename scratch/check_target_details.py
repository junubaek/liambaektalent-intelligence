import sqlite3
import pandas as pd
import sys

sys.stdout.reconfigure(encoding='utf-8')

target_names = ["이범기", "이규원", "하정근", "김연아", "권효상", "노장훈", "이효성", "김신애", "김희원"]

conn = sqlite3.connect('candidates.db')
query = f"""
SELECT id, name_kr, is_duplicate, is_parsed, 
       length(raw_text) as raw_len, 
       length(careers_json) as careers_len,
       email, current_company
FROM candidates 
WHERE name_kr IN ({','.join(['?']*len(target_names))})
ORDER BY name_kr, is_duplicate DESC
"""
df = pd.read_sql_query(query, conn, params=target_names)

print("=== Detailed Duplicate Check ===")
print(df.to_string())

conn.close()
