import sqlite3
import sys

sys.stdout.reconfigure(encoding='utf-8')
con = sqlite3.connect('candidates.db')
c = con.cursor()
c.execute("SELECT name_kr, id, is_duplicate, duplicate_of FROM candidates WHERE name_kr IN ('이준호', '이새은') AND is_duplicate = 1 LIMIT 5")
for r in c.fetchall():
    print(r)
