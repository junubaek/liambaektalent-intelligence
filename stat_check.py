import sqlite3
import pandas as pd
pd.set_option('display.max_columns', None)

conn = sqlite3.connect(r'c:\Users\cazam\Downloads\이력서자동분석검색시스템\candidates.db')
c = conn.cursor()

c.execute("SELECT COUNT(*) FROM candidates")
print("Total:", c.fetchone()[0])

c.execute("SELECT name_kr, COUNT(*) FROM candidates GROUP BY name_kr HAVING COUNT(*) > 1 ORDER BY COUNT(*) DESC")
namesakes = c.fetchall()
print("Namesakes (people):", sum(count for name, count in namesakes))
print("Namesakes (names):", len(namesakes))
print("Top Namesakes:", namesakes[:5])

c.execute("SELECT COUNT(*) FROM candidates WHERE LENGTH(CAST(raw_text AS TEXT)) < 100")
print("Raw Text < 100:", c.fetchone()[0])

c.execute("SELECT COUNT(*) FROM candidates WHERE careers_json IS NULL OR careers_json = '[]' OR careers_json = ''")
print("Careers Empty:", c.fetchone()[0])

c.execute("SELECT COUNT(*) FROM candidates WHERE (phone IS NULL OR phone='') AND (email IS NULL OR email='')")
print("Contact Empty:", c.fetchone()[0])

c.execute('''
    SELECT COUNT(*) FROM candidates 
    WHERE LENGTH(CAST(raw_text AS TEXT)) >= 100 
    AND careers_json IS NOT NULL AND careers_json != '[]' AND careers_json != ''
    AND (phone IS NOT NULL OR email IS NOT NULL)
''')
print("Perfect Data:", c.fetchone()[0])

c.execute("SELECT COUNT(*) FROM candidates WHERE (birth_year IS NULL OR birth_year='미상')")
print("Birth Year Empty:", c.fetchone()[0])

conn.close()
