import sqlite3
import json

def run_status_query():
    conn = sqlite3.connect("candidates.db")
    c = conn.cursor()
    
    # Pre-fetch valid ids
    valid_ids_rows = c.execute("SELECT id FROM candidates WHERE is_duplicate=0").fetchall()
    valid_ids = {str(r[0]).replace('-', '') for r in valid_ids_rows}
    
    with open('candidates_cache_jd.json', 'r', encoding='utf-8') as f:
        cache = json.load(f)
    cache_map = {str(item['id']).replace('-', ''): item for item in cache}
    
    # 1. 파싱 미완료 규모
    q1_1 = c.execute("SELECT COUNT(*) FROM candidates WHERE is_duplicate=0 AND (is_parsed=0 OR is_parsed IS NULL)").fetchone()[0]
    
    q1_2_summary_empty = 0
    q1_3_company_empty = 0
    
    # 2. raw_text 노출(개인정보 오염) 규모
    q2_privacy_exposure = 0
    
    for cid in valid_ids:
        data = cache_map.get(cid, {})
        # Summary
        summary = data.get('summary', '') or data.get('profile_summary', '')
        if not summary or summary.strip() == '' or summary == '정보 없음':
            q1_2_summary_empty += 1
            
        # Company
        company = data.get('current_company', '')
        if not company or company.strip() == '' or company == '미상' or company == '̻':
            q1_3_company_empty += 1
            
        # Privacy Check
        if summary and isinstance(summary, str) and summary != '정보 없음':
            patterns = ['010-', '@gmail', '@naver', '생년월일', '현 주소', '이 력 서', '이력서']
            if any(p in summary for p in patterns):
                q2_privacy_exposure += 1
                
    # 3. raw_text 자체 없는 케이스
    q3_raw_empty = c.execute("SELECT COUNT(*) FROM candidates WHERE is_duplicate=0 AND (raw_text IS NULL OR raw_text='')").fetchone()[0]
    
    print("━━━━━━━━━━━━━━━━━━━━")
    print("현황 파악 결과 리포트")
    print("━━━━━━━━━━━━━━━━━━━━")
    print("\n[ 1. 파싱 미완료 규모 ]")
    print(f"- DB상 is_parsed=0 레코드: {q1_1}명")
    print(f"- 캐시상 Summary(요약) 없는 케이스: {q1_2_summary_empty}명")
    print(f"- 캐시상 Current Company(직장) 없는 케이스: {q1_3_company_empty}명")
    
    print("\n[ 2. raw_text 노출(개인정보) 규모 ]")
    print(f"- Summary 내 개인정보 패턴 포함: {q2_privacy_exposure}명")
    
    print("\n[ 3. raw_text 자체 없는 케이스 ]")
    print(f"- 원문 텍스트(raw_text) 빈칸: {q3_raw_empty}명")

if __name__ == "__main__":
    run_status_query()
