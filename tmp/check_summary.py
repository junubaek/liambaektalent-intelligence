import sqlite3

conn = sqlite3.connect('candidates.db')
cursor = conn.cursor()

cursor.execute("SELECT count(*) FROM candidates WHERE summary IS NULL OR summary = '' OR summary = '미상' OR summary = 'None'")
blank_summary_count = cursor.fetchone()[0]

print(f"Summary (Evidence Summary) 비어있는 데이터: {blank_summary_count}명")
conn.close()
