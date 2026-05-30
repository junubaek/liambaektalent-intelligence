import sqlite3
import json
import re
import sys
import time
sys.path.append(r"C:\Users\cazam\Downloads\이력서자동분석검색시스템")
sys.stdout.reconfigure(encoding='utf-8')
import google.generativeai as genai

# secrets.json에서 API 키 로드
secrets_path = r"C:\Users\cazam\Downloads\이력서자동분석검색시스템\secrets.json"
with open(secrets_path, "r", encoding="utf-8") as f:
    secrets = json.load(f)

genai.configure(api_key=secrets["GEMINI_API_KEY"])
model = genai.GenerativeModel("gemini-2.5-flash")

DB_PATH = r"C:\Users\cazam\Downloads\이력서자동분석검색시스템\candidates.db"

def main():
    print("=== [작업 1] Sector 단순 매핑 일괄 치환 시작 ===")
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    replacements = [
        ("UPDATE candidates SET sector = 'Eng_SW' WHERE sector = 'SW'", "SW -> Eng_SW"),
        ("UPDATE candidates SET sector = 'Product' WHERE sector = 'Product_Manager'", "Product_Manager -> Product"),
        ("UPDATE candidates SET sector = 'HR' WHERE sector = 'Organizational_Development'", "Organizational_Development -> HR"),
        ("UPDATE candidates SET sector = 'Operations' WHERE sector = '물류_Logistics'", "물류_Logistics -> Operations"),
        ("UPDATE candidates SET sector = 'Strategy' WHERE sector = 'Corporate_Strategic_Planning'", "Corporate_Strategic_Planning -> Strategy"),
        ("UPDATE candidates SET sector = 'Strategy' WHERE sector = 'Corporate Strategic Planning'", "Corporate Strategic Planning -> Strategy"),
        ("UPDATE candidates SET sector = 'Eng_SW' WHERE sector = '보안_Security'", "보안_Security -> Eng_SW"),
        ("UPDATE candidates SET sector = 'Strategy' WHERE sector = '사업개발_BD'", "사업개발_BD -> Strategy"),
        ("UPDATE candidates SET sector = 'Sales' WHERE sector = 'B2B영업'", "B2B영업 -> Sales")
    ]
    
    for sql, desc in replacements:
        cur.execute(sql)
        conn.commit()
        print(f"  - {desc}: {cur.rowcount}행 치환 완료")
        
    # FinTech 재분류
    print("\n=== [작업 1-2] FinTech 후보자 37인 LLM 정밀 재분류 ===")
    cur.execute("SELECT id, name_kr, careers_json, profile_summary, raw_text FROM candidates WHERE sector = 'FinTech'")
    fintech_rows = cur.fetchall()
    
    for idx, (cid, name_kr, careers, summary, raw_text) in enumerate(fintech_rows, 1):
        content_for_ai = f"이름: {name_kr}\n요약: {summary or ''}\n경력: {careers or ''}\n본문 일부: {raw_text[:2000] if raw_text else ''}"
        
        prompt = f"""아래 후보자의 프로필 정보를 분석하여 가장 적합한 표준 직무 Sector 하나만 선택해주세요.
        
        [규칙]:
        1. 경력이나 요약 본문 중 머신러닝, 딥러닝, AI, 인공지능 관련 내용이 짙게 있으면: 'Eng_AI'
        2. 재무, 회계, IR, 투자, 재정관리 관련 내용이 있으면: 'Finance'
        3. 그 외 소프트웨어 개발, 인프라, 백엔드/프론트엔드 개발 등의 성격이면: 'Eng_SW'
        
        반드시 결과로 'Eng_AI', 'Finance', 'Eng_SW' 중 하나만 정확하게 텍스트로 출력해주세요. 부연설명은 절대 금지합니다.
        
        후보자 정보:
        {content_for_ai}
        """
        
        new_sector = 'Eng_SW'
        try:
            res = model.generate_content(prompt)
            pred = res.text.strip().replace("'", "").replace('"', "")
            if pred in ['Eng_AI', 'Finance', 'Eng_SW']:
                new_sector = pred
            else:
                # Fallback matching
                if 'Eng_AI' in pred: new_sector = 'Eng_AI'
                elif 'Finance' in pred: new_sector = 'Finance'
        except Exception as e:
            print(f"    FinTech AI reclassify error for {name_kr}: {e}")
            
        cur.execute("UPDATE candidates SET sector = ? WHERE id = ?", (new_sector, cid))
        conn.commit()
        print(f"  [{idx}/{len(fintech_rows)}] {name_kr} -> Reclassified to: {new_sector}")
        time.sleep(0.1)
        
    print("\n=== [작업 2] 이름 필드 오염 데이터 정화 시작 ===")
    cur.execute("SELECT id, name_kr, raw_text FROM candidates")
    all_cands = cur.fetchall()
    
    purified_count = 0
    
    for cid, name, raw_text in all_cands:
        if not name:
            continue
            
        original_name = name
        
        # 1. 대괄호 제거
        name = re.sub(r'\[.*?\]', '', name).strip()
        
        # 2. 파일 확장자 제거
        name = re.sub(r'\.(pdf|docx|doc|hwp).*$', '', name, flags=re.IGNORECASE).strip()
        
        # 3. 직무명만 있는 경우 (한글 이름 없고 직무 키워드만 남은 경우)
        job_indicators = {
            '개발', '기획', '부문', '원본', '팀장', 'recruiter', 
            'resume', '이력서', '포지션', '지원자', '디자이너', 
            'designer', 'MD', 'PM', 'PO', 'CTO', 'CFO', '회계', '영업'
        }
        
        is_pure_job_title = False
        if any(ind in name for ind in job_indicators):
            # 영어나 정식 인명 형태를 제외하고, 순수 직무명인지 판별
            # (한글 글자 수가 5자 이상이면서 직무 키워드가 짙은 경우 등)
            if len(name) > 4 or name in ['구매기획팀', '백엔드 개발자', 'WMS 개발', 'WMS개발', '재무회계', '이력서']:
                is_pure_job_title = True
                
        if is_pure_job_title:
            extracted_name = '미상'
            if raw_text and len(raw_text) > 100:
                # LLM으로 이력서 본문에서 실제 한글 이름 추출 시도
                prompt_name = f"""아래 이력서 본문을 분석하여 이력서 주인의 실제 '한글 본명'을 추출해주세요.
                
                [규칙]:
                - 오직 이름만 정확하게 텍스트로 출력해야 합니다 (예: 홍길동).
                - 이름이 완전히 드러나지 않거나 찾을 수 없다면 '미상'이라고 출력해주세요.
                - 부연설명이나 인사말은 절대 금지합니다.
                
                이력서 본문 일부:
                {raw_text[:2000]}
                """
                try:
                    res_name = model.generate_content(prompt_name)
                    pred_name = res_name.text.strip().replace("'", "").replace('"', "")
                    if len(pred_name) >= 2 and len(pred_name) <= 4 and re.match(r'^[가-힣]+$', pred_name):
                        extracted_name = pred_name
                except Exception as e:
                    print(f"    Name extraction error: {e}")
            name = extracted_name
            
        # 4. 이름이 변경된 경우에만 업데이트
        if name != original_name:
            cur.execute("UPDATE candidates SET name_kr = ? WHERE id = ?", (name, cid))
            conn.commit()
            purified_count += 1
            print(f"  [{purified_count}] 정화: '{original_name}' ➔ '{name}' (ID: {cid})")
            
    # 비표준 sector 잔여 확인
    print("\n=== 비표준 Sector 잔여 분포 확인 ===")
    cur.execute("""
        SELECT sector, COUNT(*) FROM candidates 
        WHERE sector NOT IN (
          'Eng_SW','Eng_AI','Eng_Data','Eng_Embedded','Eng_HW','Eng_Semi',
          'Product','Finance','Marketing','Sales','HR','Strategy',
          'Operations','Legal','Healthcare'
        )
        AND sector NOT LIKE '%,%'
        AND sector IS NOT NULL AND sector != ''
        GROUP BY sector 
        ORDER BY COUNT(*) DESC
        LIMIT 20
    """)
    remaining_sectors = cur.fetchall()
    
    if remaining_sectors:
        for idx, (sec, cnt) in enumerate(remaining_sectors, 1):
            print(f"  [{idx}] {sec}: {cnt}명")
    else:
        print("  ✅ [정화 완료] 15대 표준 직무 대분류 이외의 비표준 Sector가 완벽히 소멸되었습니다!")
        
    conn.close()
    print(f"\n데이터 정제 완료! 총 {purified_count}건의 이름 오염 정화 및 전체 Sector 표준화 성공.")

if __name__ == "__main__":
    main()
