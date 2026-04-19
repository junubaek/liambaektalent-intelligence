import sqlite3

conn = sqlite3.connect('candidates.db')
cursor = conn.cursor()

# 1. 텅 빈 이름이나 '미상' 체크
cursor.execute("SELECT count(*) FROM candidates WHERE name_kr IS NULL OR name_kr = '' OR name_kr = '미상' OR name_kr = 'Unknown'")
blank_names_count = cursor.fetchone()[0]

# 2. 직무명/포지션명이 이름으로 들어간 경우 (앞서 작성한 로직 재사용)
cursor.execute("SELECT id, name_kr, document_hash FROM candidates")
rows = cursor.fetchall()

job_keywords = ["자금", "재무", "회계", "HR", "인사", "마케팅", "영업", "Sales", "기획", 
               "개발", "디자인", "MD", "상품", "전략", "PR", "총무", "품질", "오퍼레이션", "경영"]

bad_named_ids = []
for row in rows:
    c_id, name_kr, _ = row
    if not name_kr:
        continue
    is_suspect = False
    for word in job_keywords:
        if word in name_kr and len(name_kr) <= 6 and not name_kr.endswith("님") and name_kr not in ["권기획", "이경영", "김경영", "박영업", "최디자인", "이영업"]:
            if name_kr == word or name_kr == f"{word}담당" or name_kr == f"{word}팀장" or "전문가" in name_kr:
                is_suspect = True
            elif len(name_kr) < 5 and word in name_kr:
                is_suspect = True
    if is_suspect:
        bad_named_ids.append(c_id)

bad_name_count = len(bad_named_ids)

# 3. 연락처(phone) 텅 빈 데이터 점검
cursor.execute("SELECT count(*) FROM candidates WHERE phone IS NULL OR phone = '' OR phone = '미상' OR phone = 'Unknown'")
blank_phone_count = cursor.fetchone()[0]

# 4. 현직장(current_company) 텅 빈 데이터 점검
# Note: check if current_company column exists
try:
    cursor.execute("SELECT count(*) FROM candidates WHERE current_company IS NULL OR current_company = ''")
    blank_company_count = cursor.fetchone()[0]
except sqlite3.OperationalError:
    blank_company_count = "컬럼 없음"

print("=== 데이터 품질 점검 결과 (총 2886명 기준) ===")
print(f"1. 이름이 비어있거나 '미상'인 데이터: {blank_names_count}명")
print(f"2. 직무명이 이름으로 잘못 등록된 데이터: {bad_name_count}명 (딥 리페어 대상)")
print(f"3. 연락처(전화번호)가 없는 데이터: {blank_phone_count}명")
print(f"4. 현직장/소속 정보가 없는 데이터: {blank_company_count}")

conn.close()
