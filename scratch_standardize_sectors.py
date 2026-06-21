import sqlite3

conn = sqlite3.connect('candidates.db')
cur = conn.cursor()

sector_updates = {
    '1aaad2d3-348d-48f7-8501-38d7c1f7df03': 'Eng_Semi',  # 한경환
    'fbc27466-7587-45e6-b459-c2920b5d71fe': 'Eng_SW',    # 김태경
    'e88ea471-e1eb-4c40-b5e1-7648e340fac4': 'Eng_Semi',  # 김일곤
    '31f22567-1b6f-81fd-ae6f-f34e3f501ca7': 'Eng_Semi',  # 이형덕
    'ff33752e-5e9c-4b2d-9698-f4022f2a8a57': 'Eng_SW',    # 신기욱
    '7fd23c15-b296-4bd2-a59c-eb09db05d0ef': 'Finance',   # 박민규
    '31f22567-1b6f-8152-93ca-ca5ab3080016': 'Operations',# 유정한
    '4b4c3372-401b-4897-a9b3-d36a3ba3de37': 'Finance',   # 김형수
    '32e22567-1b6f-8181-9992-d986271e941f': 'Eng_SW',    # 오수영
    '2808b157-0e3a-4454-971e-ad10b8136df6': 'Eng_SW',    # 강희성
    '07f2a68d-49b7-41e9-9c8f-e54a0e5a5482': 'Eng_Semi',  # 박상수
    'fafa2636-cf0b-42c1-8c18-598d089e9c61': 'Eng_Semi',  # 배정현
    'fcf70649-6ba3-4c6e-935b-a67eeff81094': 'Eng_AI',    # 이광욱
    'ba4abc09-302e-4fd4-ae93-b8af52aed567': 'Eng_Semi',  # 하현재
    '9a65646e-062e-4460-b402-bfa280d0d7b2': 'Eng_SW',    # 강동욱
    '32022567-1b6f-819f-b62e-fa5ecb02e3de': 'Healthcare',# 김진영
    '1c3e3279-b0c5-4661-9dcf-7fa929dd47bb': 'Finance',   # 김진호
    '3d322d13-0699-4453-b70e-5a4c2aac38f9': 'Eng_Semi',  # 박천혁
}

for cid, sec in sector_updates.items():
    cur.execute("UPDATE candidates SET sector=? WHERE id=?", (sec, cid))
    
conn.commit()
print("Candidate sectors standardized successfully in SQLite.")
conn.close()
