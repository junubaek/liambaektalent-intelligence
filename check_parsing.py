import sqlite3
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')
con = sqlite3.connect('candidates.db')
c = con.cursor()
c.execute("PRAGMA table_info(parsing_cache)")
print('parsing_cache schema:', c.fetchall())

c.execute("SELECT COUNT(*) FROM parsing_cache")
print('parsing_cache rows:', c.fetchone()[0])
