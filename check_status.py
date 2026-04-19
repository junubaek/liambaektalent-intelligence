import sqlite3
import re

def regexp(expr, item):
    if item is None:
        return False
    reg = re.compile(expr)
    return reg.search(item) is not None

conn = sqlite3.connect('candidates.db')
conn.create_function("REGEXP", 2, regexp)
cursor = conn.cursor()

query = """
SELECT 
  COUNT(*) as total,
  SUM(CASE WHEN length(name_kr) BETWEEN 2 AND 5 
    AND name_kr REGEXP '^[가-힣]+$' THEN 1 ELSE 0 END) as normal_korean,
  SUM(CASE WHEN name_kr REGEXP '[a-zA-Z]' THEN 1 ELSE 0 END) as english_included,
  SUM(CASE WHEN length(name_kr) > 5 THEN 1 ELSE 0 END) as long_string
FROM candidates
"""
cursor.execute(query)
row = cursor.fetchone()

print(f"전체: {row[0]}")
print(f"정상한국이름(2~5자): {row[1]}")
print(f"영문포함: {row[2]}")
print(f"긴이름오염(5자초과): {row[3]}")

conn.close()
