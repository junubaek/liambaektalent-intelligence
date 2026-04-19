import sqlite3
c = sqlite3.connect('candidates.db').cursor()
res = c.execute("SELECT id, name_kr FROM candidate WHERE name_kr LIKE '%전예찬%'").fetchall()
print("candidates.db matching '전예찬':", res)

import json
golden = json.load(open('golden_dataset.json', encoding='utf-8'))
items = [i for i in golden if i['candidate_name'] == '전예찬']
print("golden_dataset matching '전예찬':", items)
