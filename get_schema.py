import sqlite3
c = sqlite3.connect('candidates.db')
print(c.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='candidates'").fetchone()[0])
c.close()
