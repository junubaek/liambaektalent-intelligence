import sqlite3
import json
import sys

def main():
    sys.stdout.reconfigure(encoding='utf-8')

    conn = sqlite3.connect('candidates.db')
    cur = conn.cursor()

    cur.execute("SELECT id, careers_json, profile_summary FROM candidates WHERE sector = 'FinTech'")
    rows = cur.fetchall()
    print(f'FinTech 후보자: {len(rows)}명 재분류 시작')

    reclassify_map = []
    for id_, careers_json_str, summary in rows:
        new_sector = 'SW'  # 기본값

        try:
            career = json.loads(careers_json_str) if careers_json_str else {}
        except:
            career = {}

        skills_text = json.dumps(career, ensure_ascii=False).lower() + (summary or '').lower()

        # SW_AI로 분류
        ai_keywords = ['머신러닝', 'machine learning', 'ml ', 'deep learning', '딥러닝',
                       'llm', 'nlp', '추천 시스템', 'recommendation', '모델', 'pytorch',
                       'tensorflow', 'xgboost', 'lightgbm', '사기탐지', 'fraud detection',
                       '신용평가', 'credit scoring']
        if any(k in skills_text for k in ai_keywords):
            new_sector = 'SW_AI'

        # Finance로 분류
        finance_keywords = ['재무', 'cfo', '회계', '결산', '세무', '자금', '투자',
                            'ipo', '상장', 'ir ', '재무제표', 'ifrs', '감사',
                            '리스크 관리', 'risk management', '자산운용']
        if any(k in skills_text for k in finance_keywords):
            new_sector = 'Finance'

        reclassify_map.append((new_sector, id_))

    # 업데이트
    cur.executemany("UPDATE candidates SET sector = ? WHERE id = ?", reclassify_map)
    conn.commit()

    # 결과 확인
    from collections import Counter
    result = Counter(s for s, _ in reclassify_map)
    for sector, cnt in result.most_common():
        print(f'  → {sector}: {cnt}명')

    conn.close()
    print('완료. FinTech sector 0명으로 제거됨.')

if __name__ == '__main__':
    main()
