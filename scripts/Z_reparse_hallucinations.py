import sqlite3
import json
import time
import os
import sys
from openai import OpenAI
from neo4j import GraphDatabase
from collections import Counter

sys.stdout.reconfigure(encoding='utf-8')

def main():
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    secrets_path = os.path.join(root_dir, "secrets.json")
    cache_path = os.path.join(root_dir, "candidates_cache_jd.json")
    db_path = os.path.join(root_dir, "candidates.db")
    
    with open(secrets_path, "r", encoding='utf-8') as f:
        secrets = json.load(f)
        
    client = OpenAI(api_key=secrets.get("OPENAI_API_KEY", ""))
    neo4j_pwd = secrets.get('NEO4J_PASSWORD', 'toss1234')
    driver = GraphDatabase.driver('bolt://localhost:7687', auth=('neo4j', neo4j_pwd))
    
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    print("Loading JSON cache...")
    with open(cache_path, 'r', encoding='utf-8') as f:
        cands = json.load(f)
        
    cache_map = {str(item['id']).replace('-', ''): item for item in cands}
    
    # 1. 할루시네이션 대상자 판별
    hallucinated_ids = set()
    for cand in cands:
        careers = cand.get('parsed_career_json') or []
        companies = [x.get('company','') for x in careers if x.get('company')]
        dupes = [co for co, cnt in Counter(companies).items() if cnt >= 2]
        if dupes:
            hallucinated_ids.add(str(cand['id']).replace('-', ''))
            
    print(f"Targeting {len(hallucinated_ids)} hallucinated candidates for reparsing...")
    if not hallucinated_ids:
        print("No hallucination bugs found! Exiting.")
        return
        
    print("Fetching raw_texts from SQLite...")
    c.execute("SELECT id, name_kr, raw_text FROM candidates WHERE is_duplicate=0")
    targets = c.fetchall()
    
    to_parse = []
    for row in targets:
        cid_str = str(row[0]).replace('-', '')
        if cid_str in hallucinated_ids:
            cinfo = cache_map.get(cid_str)
            if not cinfo: continue
            raw_text = cinfo.get("raw_text", row[2] or "")
            if len(raw_text) > 100:
                to_parse.append((cid_str, row[1], raw_text))
                
    total = len(to_parse)
    print(f"Found {total} candidates ready for valid reparsing.")
    
    system_prompt = """당신은 최고 수준의 이력서 분석 시스템입니다. 
    아래 주어진 이력서 텍스트를 분석하여 정확한 JSON 객체를 반환하세요.
    응답은 반드시 아래 JSON 스키마를 준수해야 합니다.
    
    [작성 가이드]
    1. 이메일, 전화번호(010-), 시니어리티(Junior/Middle/Senior)가 명시되어 있다면 해당 필드에 정확히 추출하세요. 없으면 빈 문자열("")을 반환하세요.
    2. careers 항목에는 회사에서의 경력 배열을 10개 내로 요약해서 넣으세요.
       - 단, 반드시 "company" (회사명), "team" (부서/팀명), "position" (직무/직책), "period" (기간) 4개의 키를 가져야 합니다.
       - 기간 형식은 'YYYY.MM ~ YYYY.MM' 또는 'YYYY.MM ~ 현재' 형태로 통일하세요.
       
    [parsed_career_json 필수 규칙]
    - 동일한 company명은 반드시 1개 객체로만 기록하세요. 여러 프로젝트가 있어도 동일 회사면 하나로 병합하여 하나의 block으로 취급하십시오.
    - careers 배열 내 company 원소 중복은 절대 금지됩니다. (Deduplication 원칙)
    - 최대 항목 수: 10개 내외가 아닌, 후보자의 실제 재직 회사 개수와 정확히 일치하게 뽑으세요.
    """
    
    success = 0
    fail = 0
    session = driver.session()
    
    for i, (cid_str, name, raw_text) in enumerate(to_parse):
        clean_text = ' '.join((raw_text[:6000]).split())
        
        try:
            res = client.chat.completions.create(
                model="gpt-4o-mini",
                response_format={ "type": "json_object" },
                timeout=15,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"이력서 텍스트:\n{clean_text}"}
                ]
            )
            parsed_data = json.loads(res.choices[0].message.content)
            careers = parsed_data.get("careers", [])
            
            if not isinstance(careers, list):
                careers = []
                
            cinfo = cache_map[cid_str]
            cinfo["parsed_career_json"] = careers
            
            career_str = json.dumps(careers, ensure_ascii=False)
            session.run("MATCH (c:Candidate {id: $id}) SET c.parsed_career_json = $data", id=cid_str, data=career_str)
            
            success += 1
            print(f"Parsed {cid_str} ({success}/{total})", flush=True)
            if (i+1) % 5 == 0:
                print(f"Progress: {i+1}/{total} | Success: {success} | Fail: {fail}", flush=True)
                
        except Exception as e:
            fail += 1
            print(f"Error for {cid_str}: {e}")
            time.sleep(2)
            
    session.close()
    
    print("\nSaving updated JSON cache...")
    with open(cache_path, 'w', encoding='utf-8') as f:
        json.dump(cands, f, ensure_ascii=False, indent=2)
        
    print(f"✅ Hallucination Reparse Complete! Total Success: {success}")

if __name__ == '__main__':
    main()
