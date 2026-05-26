import sqlite3
import pandas as pd
import sys

sys.stdout.reconfigure(encoding='utf-8')

target_names = ["이범기", "이규원", "하정근", "김연아", "권효상", "노장훈", "이효성", "김신애", "김희원"]

conn = sqlite3.connect('candidates.db')
query = f"SELECT id, name_kr, email, current_company, is_parsed, is_duplicate, duplicate_of, source_file FROM candidates WHERE name_kr IN ({','.join(['?']*len(target_names))})"
df = pd.read_sql_query(query, conn, params=target_names)

print("=== SQLite Candidates ===")
if df.empty:
    print("No records found.")
else:
    print(df.to_string())
conn.close()
