import sqlite3
import sys
sys.stdout.reconfigure(encoding='utf-8')

conn = sqlite3.connect('candidates.db')
cur = conn.cursor()

print("=== Starting Final Fixes ===")

# 1. Name Fixes
# '장현' -> '성장현'
cur.execute("UPDATE candidates SET name_kr = '성장현' WHERE id = '33522567-1b6f-812a-9643-fa927de1cf02'")
print("Fixed '장현' -> '성장현'")

# '마켓보로' -> '김형수'
cur.execute("UPDATE candidates SET name_kr = '김형수' WHERE id = '32022567-1b6f-81ba-9fab-c5090b7b3158'")
print("Fixed '마켓보로' -> '김형수'")

# 2. Company Updates
# 조예원 -> 해피문데이
cur.execute("UPDATE candidates SET current_company = '해피문데이' WHERE id = 'af3acee5-6ed7-4111-8b5f-f0d1145969e7'")
print("Updated 조예원 Company: 해피문데이")

# 남현승 -> Pagoda Academy
cur.execute("UPDATE candidates SET current_company = 'Pagoda Academy' WHERE id = '3d01296a-b15c-4525-9aa1-e4f1b8cb7cc8'")
print("Updated 남현승 Company: Pagoda Academy")

# 3. Master Alignment (is_duplicate = 0 for record with company info)
# 이민지
cur.execute("UPDATE candidates SET is_duplicate = 0 WHERE id = '6004cf18-e163-4735-a364-b8ce9ce19319'") # (주)네오위즈랩
cur.execute("UPDATE candidates SET is_duplicate = 1 WHERE id = '33522567-1b6f-8128-8472-f3797d94e5b6'") # None
print("Aligned 이민지 Master/Duplicate")

# 권슬기
cur.execute("UPDATE candidates SET is_duplicate = 0 WHERE id = '3483a2f4-9534-4faf-a6bc-3db136b21390'") # 주식회사케이엘유피
cur.execute("UPDATE candidates SET is_duplicate = 1 WHERE id = '32022567-1b6f-812b-b7ce-f838672de47e'") # None
print("Aligned 권슬기 Master/Duplicate")

# 손민정
cur.execute("UPDATE candidates SET is_duplicate = 0 WHERE id = '9f1c353e-a74e-4c89-8249-606e97ddcc9b'") # (주)쁘띠엘린
cur.execute("UPDATE candidates SET is_duplicate = 1 WHERE id = '32022567-1b6f-81b1-8aec-c70d657984ab'") # ''
print("Aligned 손민정 Master/Duplicate")

conn.commit()
conn.close()
print("=== Final Fixes Applied Successfully ===")
