import sqlite3
import json
import sys

def regenerate_cache():
    conn = sqlite3.connect('candidates.db')
    cur = conn.cursor()
    cur.execute('''SELECT id, name_kr, sector, profile_summary, current_company,
                   total_years, email, phone, birth_year, google_drive_url,
                   careers_json, education_json
                   FROM candidates WHERE is_duplicate=0''')
    rows = cur.fetchall()

    cache_list = []
    for r in rows:
        cid, name, sector, summary, company, years, email, phone, birth, gdrive, careers, edu = r
        careers_list = []
        edu_list = []
        try:
            if careers: careers_list = json.loads(careers)
        except: pass
        try:
            if edu: edu_list = json.loads(edu)
        except: pass
        
        cache_list.append({
            'id': cid,
            'name_kr': name,
            'sector': sector or '미분류',
            'profile_summary': summary or '',
            'current_company': company or '',
            'total_years': years or 0,
            'email': email or '',
            'phone': phone or '',
            'birth_year': birth or '',
            'google_drive_url': gdrive or '',
            'careers': careers_list,
            'parsed_career_json': careers_list,
            'education': edu_list,
            'main_sectors': [sector] if sector else []
        })

    with open('candidates_cache_jd.json', 'w', encoding='utf-8') as f:
        json.dump(cache_list, f, ensure_ascii=False, indent=2)

    conn.close()
    print(f"JSON 캐시 리스트 재생성 완료: {len(cache_list)}명")

    # 김국현, 이원철, 한상현 확인
    for data in cache_list:
        if data['name_kr'] in ['김국현','이원철','한상현']:
            print(f"{data['name_kr']}: sector={data['sector']}, company={data['current_company']}")
            print(f"  summary={data['profile_summary'][:60]}")

if __name__ == "__main__":
    regenerate_cache()
