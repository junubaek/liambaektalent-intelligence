import sqlite3
import sys

sys.stdout.reconfigure(encoding='utf-8')
con = sqlite3.connect('candidates.db')
c = con.cursor()
c.execute("PRAGMA table_info(candidates)")
for r in c.fetchall():
    print(r)
