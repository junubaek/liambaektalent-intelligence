import sqlite3, sys
sys.stdout.reconfigure(encoding='utf-8')
conn = sqlite3.connect('candidates.db')
cur = conn.cursor()
cur.execute('SELECT raw_text FROM candidates WHERE name_kr = "강기태" AND is_duplicate = 0')
row = cur.fetchone()
if not row:
    print("Candidate not found.")
    sys.exit(1)

text = row[0]
keywords = ['Global', 'Sales', 'Marketing', 'Financial', 'Accounting', 'Banking', 'Credit', 'Retail', 'SCM', 'Commerce', 'HR', 'Payroll']
print('[Keyword Frequency in Kang Ki-tae Resume]')
for kw in keywords:
    count = text.lower().count(kw.lower())
    print(f' - {kw}: {count}')

# Context check for keywords found
for kw in keywords:
    idx = text.lower().find(kw.lower())
    if idx != -1:
        print(f'\nContext ({kw}): ...{text[max(0, idx-50):idx+100]}...')
        
conn.close()
