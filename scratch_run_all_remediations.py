import sqlite3
import json
import re
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from openai import OpenAI
from neo4j import GraphDatabase
from ontology_graph import CANONICAL_MAP

# UTF-8 출력 설정
sys.stdout.reconfigure(encoding='utf-8')

# API & DB 커넥션 로드
secrets = json.load(open('secrets.json', encoding='utf-8'))
oai = OpenAI(api_key=secrets['OPENAI_API_KEY'])

def get_db_conn():
    conn = sqlite3.connect('candidates.db')
    conn.row_factory = sqlite3.Row
    return conn

# =========================================================================
# 1. [약점 2-A] 오염된 name_kr 즉시 정리
# =========================================================================
print("=== [1] [약점 2-A] 오염된 name_kr 즉시 정리 ===")
conn = get_db_conn()
cur = conn.cursor()

# [A] 특정 오염 키워드 즉시 중복 마킹
cur.execute("""
    UPDATE candidates SET is_duplicate = 1
    WHERE name_kr IN ('재무회계', '원본', 'UX컨설팅', '연구개발 차량설계')
""")
conn.commit()
print("  - '재무회계', '원본', 'UX컨설팅', '연구개발 차량설계' -> is_duplicate = 1 마킹 완료.")

# [B] name_kr이 순수 영문 2단어 이상이면서 비정상적인 레코드 검사 및 출력
cur.execute("""
    SELECT id, name_kr, profile_summary, current_company
    FROM candidates
    WHERE is_duplicate = 0
""")
active_rows = cur.fetchall()

suspicious_english_names = []
for row in active_rows:
    name_kr = row['name_kr']
    summary = row['profile_summary'] or ''
    company = row['current_company'] or ''
    
    # 20자 이상이면서 한글이 없고 영문인 경우
    if name_kr and len(name_kr) > 20 and not re.search('[가-힣]', name_kr):
        # 영문 2단어 이상 체크 (공백이나 특수문자로 분리)
        words = re.split(r'\s+', name_kr.strip())
        if len(words) >= 2 and (not company or len(summary) < 10):
            suspicious_english_names.append((row['id'], name_kr, summary[:30]))

print(f"\n--- [검사결과] name_kr 오염 의심 영문 후보군 현황 (총 {len(suspicious_english_names)}건) ---")
for idx, (cid, name_kr, summ) in enumerate(suspicious_english_names[:20], 1):
    print(f"  {idx}. ID: {cid} | Name: {name_kr} | Summary Preview: {summ}...")
if len(suspicious_english_names) > 20:
    print(f"  ...외 {len(suspicious_english_names) - 20}건 더 있음.")
print("  (지침에 따라 직접 처리는 하지 않고 조회 결과만 출력하였습니다.)\n")

conn.close()


# =========================================================================
# 2. [약점 3] 영문 이력서 36명 한글 요약 자동 생성
# =========================================================================
print("=== [2] [약점 3] 영문 이력서 한글 요약 자동 생성 ===")
conn = get_db_conn()
cur = conn.cursor()

cur.execute("""
    SELECT id, name_kr, profile_summary
    FROM candidates
    WHERE is_duplicate = 0
    AND profile_summary IS NOT NULL
""")
candidates_summary = cur.fetchall()

eng_targets = []
for cand in candidates_summary:
    name_kr = cand['name_kr']
    # name_kr에 한글이 한 글자도 없으면 영문 이력서 후보군으로 판단
    if not name_kr or not re.search('[가-힣]', name_kr):
        eng_targets.append((cand['id'], cand['profile_summary']))

print(f"  - 한글 요약 대상 영문 후보자: {len(eng_targets)}명")

def summarize_english_profile(cid, eng_summary):
    prompt = f"""다음 영문 프로필을 한국어로 100자 이내로 요약해줘.
현재 회사, 핵심 직무, 주요 기술 스택 중심으로 요약하고, 불필요한 서술어 없이 간결하게 단답형 문장들로 구성해줘.

영문 프로필:
{eng_summary}"""
    try:
        resp = oai.chat.completions.create(
            model='gpt-4o-mini',
            messages=[{'role': 'user', 'content': prompt}],
            temperature=0.3,
            max_tokens=150
        )
        ko_summary = resp.choices[0].message.content.strip()
        return cid, ko_summary
    except Exception as e:
        return cid, None

translated_count = 0
if eng_targets:
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = {executor.submit(summarize_english_profile, cid, summ): cid for cid, summ in eng_targets}
        for fut in as_completed(futures):
            cid, ko_summary = fut.result()
            if ko_summary:
                cur.execute("UPDATE candidates SET profile_summary = ? WHERE id = ?", (ko_summary, cid))
                translated_count += 1

conn.commit()
conn.close()
print(f"  - 영문 이력서 한글 요약 적용 완료: {translated_count}명\n")


# =========================================================================
# 3. [약점 4] profile_summary 짧은 500명 보강
# =========================================================================
print("=== [3] [약점 4] profile_summary 짧은 500명 보강 ===")
conn = get_db_conn()
cur = conn.cursor()

# 50자 미만이거나 Null인 활성 후보자 500명 선정
cur.execute("""
    SELECT id, name_kr, raw_text
    FROM candidates
    WHERE is_duplicate = 0
    AND (profile_summary IS NULL OR length(profile_summary) < 50)
    AND raw_text IS NOT NULL
    AND length(raw_text) > 100
    LIMIT 500
""")
enrichment_targets = cur.fetchall()
print(f"  - 보강 대상 후보자: {len(enrichment_targets)}명")

def generate_profile_summary(cid, raw_text):
    prompt = f"""다음 이력서에서 핵심 정보를 150자 이내 한국어로 요약해줘.
현재 회사, 연차, 핵심 직무, 주요 성과 중심으로 개조식 혹은 간결한 문장으로 요약해줘.

이력서 본문:
{raw_text[:2000]}"""
    try:
        resp = oai.chat.completions.create(
            model='gpt-4o-mini',
            messages=[{'role': 'user', 'content': prompt}],
            temperature=0.3,
            max_tokens=200
        )
        summary = resp.choices[0].message.content.strip()
        return cid, summary
    except Exception as e:
        return cid, None

enriched_count = 0
if enrichment_targets:
    # 30 workers 병렬 처리
    with ThreadPoolExecutor(max_workers=30) as executor:
        futures = {executor.submit(generate_profile_summary, r['id'], r['raw_text']): r['id'] for r in enrichment_targets}
        for fut in as_completed(futures):
            cid, summary = fut.result()
            if summary:
                cur.execute("UPDATE candidates SET profile_summary = ? WHERE id = ?", (summary, cid))
                enriched_count += 1

conn.commit()
conn.close()
print(f"  - profile_summary 보강 적용 완료: {enriched_count}명\n")


# =========================================================================
# 4. [약점 2-B] 엣지 없는 1,197명 자동 엣지 생성
# =========================================================================
print("=== [4] [약점 2-B] 엣지 없는 1,197명 자동 엣지 생성 ===")
try:
    driver = GraphDatabase.driver(secrets['NEO4J_URI'],
        auth=(secrets['NEO4J_USERNAME'], secrets['NEO4J_PASSWORD']))

    # 엣지 없는 후보자 ID 목록 조회
    with driver.session() as s:
        r = s.run("""
            MATCH (c:Candidate)
            WHERE NOT (c)-[]->(:Skill)
            RETURN c.id as id, c.name_kr as name_kr
        """)
        no_edge = [(row['id'], row['name_kr']) for row in r]

    print(f'  - Neo4j 기준 엣지 없는 후보자: {len(no_edge)}명')

    conn = get_db_conn()
    cur = conn.cursor()

    # 스킬 스캔 키워드 준비
    canonical_keys = sorted(CANONICAL_MAP.keys(), key=len, reverse=True)

    added = 0
    skipped = 0

    with driver.session() as session:
        for cid, name_kr in no_edge:
            if not cid:
                skipped += 1
                continue
            cur.execute(
                'SELECT profile_summary, sector FROM candidates WHERE id=? AND is_duplicate=0',
                (cid,))
            row = cur.fetchone()
            if not row or not row[0]: 
                skipped += 1
                continue
            
            summary = row[0].lower()
            
            # 스킬 추출
            found_skills = []
            for key in canonical_keys:
                if key.lower() in summary and len(key) >= 3:
                    canonical_id = CANONICAL_MAP[key]
                    if canonical_id not in found_skills:
                        found_skills.append(canonical_id)
                if len(found_skills) >= 5:
                    break
            
            if not found_skills:
                skipped += 1
                continue
            
            # Neo4j에 BUILT 엣지 생성
            try:
                for skill in found_skills:
                    session.run("""
                        MATCH (c:Candidate {id: $cid})
                        MERGE (s:Skill {name: $skill})
                        MERGE (c)-[:BUILT {weight: 0.7, auto_generated: true, last_used_year: 2025}]->(s)
                    """, cid=cid, skill=skill)
                added += 1
            except Exception as e:
                skipped += 1

    conn.close()
    driver.close()
    print(f'  - Neo4j 엣지 자동 복구 완료: {added}명 추가, {skipped}명 스킵')
except Exception as e:
    print("  - Neo4j 작업 실패:", str(e))

print("\nRemediation 스크립트 실행 완료!")
