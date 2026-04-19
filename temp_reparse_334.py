import os
import sys
sys.stdout.reconfigure(encoding='utf-8')
import json
import asyncio
from collections import Counter
import sqlite3
from neo4j import GraphDatabase

from jd_compiler import client as genai_client
from google.genai import types

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
CACHE_FILE = os.path.join(ROOT_DIR, "candidates_cache_jd.json")
SECRETS_FILE = os.path.join(ROOT_DIR, "secrets.json")
DB_PATH = os.path.join(ROOT_DIR, "candidates.db")

with open(SECRETS_FILE, "r", encoding="utf-8") as f:
    secrets = json.load(f)

neo4j_pwd = secrets.get('NEO4J_PASSWORD', 'toss1234')
driver = GraphDatabase.driver('bolt://localhost:7687', auth=('neo4j', neo4j_pwd))

system_prompt = """당신은 최고 수준의 데이터 정밀도를 지향하는 리크루팅 어시스턴트입니다. 
아래의 비정형 이력 텍스트를 분석하여 구조화된 JSON 형태로 변환하세요.

[무결성 가이드라인]
1. 연락처/기본정보 추출: 이력서 내에 이메일, 전화번호(010-), 연차(seniority)가 명시되어 있다면 해당 필드에 정확히 담아주세요. 없다면 빈 문자열("")로 반환하세요.
2. 날짜 무결성 (가장 중요): 근무 기간(연/월)이 기재된 경우 '단 하나도 빠짐없이 전부' 추출하여 period 필드에 기재하세요. (예: '2022.08 ~ 현재').
3. 직급 표준화: 원문의 직급/직무를 기재하세요.
4. 전체 경력 추출 (가장 중요): 제공된 이력서 텍스트 안에 회사가 여러개라면 전부를 빠짐없이 careers 리스트에 담아 추출하세요.

[parsed_career_json 규칙]
- 동일한 company명은 반드시 1개 객체로만 기록. 여러 프로젝트가 있어도 동일 회사면 하나로 병합.
- 배열 내 company 중복 절대 금지.
- 최대 항목 수: 실제 재직 회사 수와 동일하게.

반드시 다음 JSON 스키마를 준수해야 합니다.
{
    "careers": [
        {"company": "string", "team": "string", "position": "string", "period": "string"}
    ]
}"""

async def extract_one(sem, cid, clean_text):
    config = types.GenerateContentConfig(
        response_mime_type="application/json",
        system_instruction=system_prompt,
        temperature=0.0
    )
    async with sem:
        try:
            res = await genai_client.aio.models.generate_content(
                model="gemini-2.5-flash",
                contents=[f'분석 대상 텍스트: "{clean_text}"'],
                config=config
            )
            data = json.loads(res.text)
            return cid, data.get("careers", [])
        except Exception as e:
            return cid, str(e)

async def main():
    with open(CACHE_FILE, "r", encoding="utf-8") as f:
        cands = json.load(f)

    # 1. 대상 추출
    hallucinated_ids = set()
    for c in cands:
        careers = c.get('parsed_career_json') or []
        if isinstance(careers, str):
            try: careers = json.loads(careers)
            except: pass
        companies = [x.get('company','') for x in careers if isinstance(x, dict) and x.get('company')]
        dupes = [co for co, cnt in Counter(companies).items() if cnt >= 2]
        if dupes: hallucinated_ids.add(c.get('id'))

    print(f"🚀 재파싱 시도 개수: {len(hallucinated_ids)}명")
    
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT id, raw_text FROM candidates")
    raw_texts = {row[0]: row[1] for row in cur.fetchall()}
    
    tasks = []
    sem = asyncio.Semaphore(15)
    for c in cands:
        cid = c.get('id')
        if cid in hallucinated_ids:
            raw_text = raw_texts.get(cid)
            if not raw_text or len(raw_text) < 50: raw_text = c.get("summary", "")
            clean_text = ' '.join(raw_text.split())[:8000]
            if clean_text:
                tasks.append(extract_one(sem, cid, clean_text))
                
    print("⏳ Gemini 병렬 파싱 진행 중...")
    results = await asyncio.gather(*tasks)
    
    success = 0
    with driver.session() as session:
        result_map = {k: v for k, v in results}
        for c in cands:
            cid = c.get('id')
            if cid in result_map:
                careers = result_map[cid]
                if isinstance(careers, list):
                    c["parsed_career_json"] = careers
                    career_str = json.dumps(careers, ensure_ascii=False)
                    session.run("MATCH (n:Candidate {id: $id}) SET n.parsed_career_json = $data", id=cid, data=career_str)
                    success += 1
                else:
                    print(f"❌ Fail {cid}: {careers}")
                    
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(cands, f, ensure_ascii=False, indent=2)

    print(f"✅ 완료! 성공 재파싱: {success}건")
    
    for c in cands:
        if c.get('name_kr') == '임형욱':
            print(f"=== [임형욱] 점검 ===")
            print(json.dumps(c.get('parsed_career_json'), ensure_ascii=False, indent=2))

if __name__ == "__main__":
    asyncio.run(main())
