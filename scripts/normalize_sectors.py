import sqlite3, sys
sys.stdout.reconfigure(encoding='utf-8')

# ── 표준 sector 정의 ──────────────────────────────
# Primary, Secondary 최대 2개. 첫 번째가 주전공.
# 형식: "Primary" 또는 "Primary, Secondary"

SECTOR_MAP = {
    # SW 계열
    'SW': 'Eng_SW',
    'SW (Software)': 'Eng_SW',
    'IT/플랫폼': 'Eng_SW',
    'Backend': 'Eng_SW',
    'Infrastructure_and_Cloud': 'Eng_SW',

    # AI 계열
    'SW_AI': 'Eng_AI',
    'Machine_Learning': 'Eng_AI',
    'Deep_Learning': 'Eng_AI',

    # Data 계열
    'Data_Analysis': 'Eng_Data',

    # Embedded 계열
    'SW_Systems': 'Eng_Embedded',

    # HW 계열
    'HW (Hardware)': 'Eng_HW',
    'Engineering': 'Eng_HW',
    'Manufacturing': 'Eng_HW',

    # Semiconductor 계열
    'Semiconductor_SoC': 'Eng_Semi',
    'Semiconductor_NPU': 'Eng_Semi, Eng_AI',
    'Semiconductor': 'Eng_Semi',

    # Business 계열
    'Finance': 'Finance',
    'Finance (재무/회계)': 'Finance',
    'Financial_Accounting': 'Finance',
    'Strategy': 'Strategy',
    'Corporate_Strategic_Planning': 'Strategy',
    'Corporate Strategic Planning': 'Strategy',
    '사업개발_BD': 'Strategy, Sales',
    'Marketing': 'Marketing',
    'Sales': 'Sales',
    'B2B영업': 'Sales',
    '영업 (Sales)': 'Sales',
    'Operations': 'Operations',
    '물류_Logistics': 'Operations',
    'Logistics': 'Operations',
    'HR': 'HR',
    'Human Resources': 'HR',
    'Organizational_Development': 'HR',
    'Recruiting_and_Talent_Acquisition': 'HR',
    'Legal': 'Legal',
    'Healthcare': 'Healthcare',
    'Product_Manager': 'Product',
    'Service_Planning': 'Product',
    '보안_Security': 'Eng_SW',
}

conn = sqlite3.connect(
    r'C:\Users\cazam\Downloads\이력서자동분석검색시스템\candidates.db'
)
cur = conn.cursor()

# 현재 sector 값 전체 가져오기
cur.execute("SELECT id, sector FROM candidates")
rows = cur.fetchall()

mapped, unmapped = 0, []
updates = []

for id_, sector in rows:
    if not sector:
        unmapped.append((id_, sector))
        continue
    if sector in SECTOR_MAP:
        updates.append((SECTOR_MAP[sector], id_))
        mapped += 1
    else:
        unmapped.append((id_, sector))

# 매핑된 것 업데이트
cur.executemany("UPDATE candidates SET sector = ? WHERE id = ?", updates)
conn.commit()

print(f'매핑 완료: {mapped}명')
print(f'미매핑 (수동 확인 필요): {len(unmapped)}명')
print('\n=== 미매핑 sector 목록 ===')
from collections import Counter
unmapped_sectors = Counter(s for _, s in unmapped if s)
for sector, cnt in unmapped_sectors.most_common(30):
    print(f'  {sector}: {cnt}명')

conn.close()
