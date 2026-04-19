import os
import re

# 1. Update dynamic_parser.py
with open("dynamic_parser.py", "r", encoding="utf-8") as f:
    dynamic_code = f.read()

# Split dynamic_parser.py at 'def parse_resume(text):'
head, _ = dynamic_code.split("def parse_resume(text):", 1)

new_dynamic_body = """def parse_resume(text):
    if not text or len(text) < 100:
        return []
    
    prompt = f\"\"\"
이력서 텍스트에서 후보자가 실제로 수행한 행위를 추출해줘.
반드시 아래 JSON 배열 형식으로만 응답해. 다른 텍스트 없이.

형식:
[
  {{"action": "BUILT", "skill": "Payment_and_Settlement_System"}},
  {{"action": "DESIGNED", "skill": "Data_Pipeline_Construction"}}
]

action은 다음 중 하나만 사용:
- BUILT: 직접 구축/개발/만든 경우
- DESIGNED: 설계/기획한 경우  
- MANAGED: 관리/운영한 경우
- ANALYZED: 분석한 경우
- SUPPORTED: 보조/지원한 경우

skill은 아래 목록 중에서만 선택:
Payment_and_Settlement_System, Service_Planning, Product_Manager,
Data_Pipeline_Construction, Data_Engineering, Data_Analysis,
Backend, Frontend, Machine_Learning, MLOps, DevOps,
Financial_Accounting, Corporate_Strategic_Planning, 사업개발_BD, 퍼포먼스마케팅,
Treasury_Management, FX_Dealing, Corporate_Funding, IPO_Preparation_and_Execution,
Recruiting_and_Talent_Acquisition, Organizational_Development, B2B영업, 물류_Logistics,
Backend_Python, Backend_Java, Backend_Go, Backend_Node,
Kubernetes, Infrastructure_and_Cloud, 보안_Security, FinTech,
Natural_Language_Processing, 컴퓨터비전_CV, 추천시스템, Deep_Learning

이력서:
{text[:3000]}
\"\"\"
    import time
    import json
    for attempt in range(3):
        try:
            response = model.generate_content(prompt)
            raw = response.text.strip()
            raw = raw.replace("```json", "").replace("```", "").strip()
            return json.loads(raw)
        except Exception as e:
            err_str = str(e)
            if "429" in err_str or "Quota" in err_str or "exhausted" in err_str.lower():
                time.sleep(10)
            else:
                break
    return []

def parse_resume_batch(batch_dict):
    \"\"\"
    batch_dict: dict of {name: text} (up to 5 items)
    Returns: dict of {name: edges_list}
    \"\"\"
    import json, time
    if not batch_dict: return {}
    
    # 텍스트 길이 제한 (각 1500자)
    combined_texts = []
    for name, text in batch_dict.items():
        combined_texts.append(f"======\\n[후보자명: {name}]\\n{text[:1500]}\\n======")
        
    combined_body = "\\n".join(combined_texts)
    
    prompt = f\"\"\"
아래 여러 명의 이력서를 분석하여 각각 수행한 행위를 추출해.
반드시 아래 JSON Object 형식으로만 응답해. 키값은 대괄호 안의 후보자명과 정확히 일치해야 해.

형식:
{{
  "후보자A": [ {{"action": "BUILT", "skill": "Payment_and_Settlement_System"}} ],
  "후보자B": [ {{"action": "DESIGNED", "skill": "Data_Pipeline_Construction"}} ]
}}

action은 반드시 [BUILT, DESIGNED, MANAGED, ANALYZED, SUPPORTED] 중 하나만 사용.

skill은 반드시 아래 목록 내에서만 선택:
Payment_and_Settlement_System, Service_Planning, Product_Manager,
Data_Pipeline_Construction, Data_Engineering, Data_Analysis,
Backend, Frontend, Machine_Learning, MLOps, DevOps,
Financial_Accounting, Corporate_Strategic_Planning, 사업개발_BD, 퍼포먼스마케팅,
Treasury_Management, FX_Dealing, Corporate_Funding, IPO_Preparation_and_Execution,
Recruiting_and_Talent_Acquisition, Organizational_Development, B2B영업, 물류_Logistics,
Backend_Python, Backend_Java, Backend_Go, Backend_Node,
Kubernetes, Infrastructure_and_Cloud, 보안_Security, FinTech,
Natural_Language_Processing, 컴퓨터비전_CV, 추천시스템, Deep_Learning

제시된 이력서들:
{combined_body}
\"\"\"
    for attempt in range(3):
        try:
            response = model.generate_content(prompt)
            raw = response.text.strip()
            raw = raw.replace("```json", "").replace("```", "").strip()
            parsed = json.loads(raw)
            return parsed
        except Exception as e:
            err_str = str(e)
            if "429" in err_str or "Quota" in err_str or "exhausted" in err_str.lower():
                time.sleep(10)
            else:
                break
    return {}

# ── Neo4j 저장 ─────────────────────────────────────
def save_edges(candidate_name, edges):
    if not edges:
        return
    with driver.session() as session:
        for edge in edges:
            action = edge.get("action", "").upper()
            skill = edge.get("skill", "")
            if not action or not skill:
                continue
            session.run(f\"\"\"
                MERGE (c:Candidate {{name: $name}})
                MERGE (s:Skill {{name: $skill}})
                MERGE (c)-[r:{action}]->(s)
                SET r.source = 'llm_parsed'
            \"\"\", name=candidate_name, skill=skill)

# ── 진행상황 관리 ──────────────────────────────────
def load_progress():
    import json, os
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE) as f:
            return set(json.load(f))
    return set()

def save_progress(processed):
    import json
    with open(PROGRESS_FILE, "w") as f:
        json.dump(list(processed), f)

# ── 파일 목록 수집 ─────────────────────────────────
def collect_files():
    import os
    files = {}
    if os.path.exists(FOLDER1):
        for f in os.listdir(FOLDER1):
            name = f.rsplit(".", 1)[0]
            files[name] = os.path.join(FOLDER1, f)
    if os.path.exists(FOLDER2):
        for f in os.listdir(FOLDER2):
            name = f.rsplit(".", 1)[0]
            files[name] = os.path.join(FOLDER2, f)
    return files

# ── 메인 실행 ──────────────────────────────────────
def main():
    import time
    files = collect_files()
    processed = load_progress()
    remaining = {k: v for k, v in files.items() if k not in processed}
    
    remaining = {k: v for k, v in remaining.items() if str(v).lower().endswith('.pdf') or str(v).lower().endswith('.docx')}
    
    print(f"전체: {len(files)}개 / 완료: {len(processed)}개 / 대상: {len(remaining)}개")
    
    # Batch Processing Logic
    remaining_items = list(remaining.items())
    batch_size = 5
    
    for i in tqdm(range(0, len(remaining_items), batch_size)):
        chunk = remaining_items[i : i+batch_size]
        batch_dict = {}
        for name, filepath in chunk:
            text = extract_text(filepath)
            if len(text) >= 100:
                batch_dict[name] = text
            else:
                processed.add(name)  # skip empty
        
        if not batch_dict:
            continue
            
        print(f"\\n[Batch Parsing] {list(batch_dict.keys())}")
        batch_results = parse_resume_batch(batch_dict)
        
        # Fallback Check
        for name in batch_dict.keys():
            if name in batch_results:
                edges = batch_results[name]
                save_edges(name, edges)
                processed.add(name)
            else:
                # LLM Omission Fallback
                print(f"\\n[Fallback] {name} 누락 감지. 개별 처리 재시도...")
                edges = parse_resume(batch_dict[name])
                save_edges(name, edges)
                processed.add(name)
                
        if len(processed) % 10 < batch_size:  # Approximate save step
            save_progress(processed)
            
        time.sleep(1)
        
    save_progress(processed)
    print("완료!")

if __name__ == "__main__":
    main()
"""

with open("dynamic_parser.py", "w", encoding="utf-8") as f:
    f.write(head + new_dynamic_body)

# 2. Update jd_compiler.py parsing function for cache
with open("jd_compiler.py", "r", encoding="utf-8") as f:
    jd_code = f.read()

new_parse_jd_func = """import hashlib
import os
import json

def parse_jd_to_json(jd_text: str) -> dict:
    JD_CACHE_FILE = "jd_cache.json"
    h = hashlib.md5(jd_text.strip().encode('utf-8')).hexdigest()
    
    # Check cache
    if os.path.exists(JD_CACHE_FILE):
        with open(JD_CACHE_FILE, "r", encoding="utf-8") as f:
            cache = json.load(f)
            if h in cache:
                logger.info("[Cache Hit] JD 파싱 결과를 로컬 캐시에서 불러왔습니다.")
                return cache[h]

    # ... 기존 프롬프트 실행 ...
    logger.info("Extracting intents via Gemini...")
    prompt = f\"\"\"
    다음은 채용공고(JD) 텍스트입니다. 이 JD에서 요구하는 구체적 행위(action)와 기술(skill), 그리고 요구 경력(최소 연차)를 추출해주세요.
    반드시 JSON 형식으로만 응답해야 하며, 아래 스키마를 엄격히 지켜주세요.
    
    {{
      "min_years": 0, // JD에서 요구하는 최소 연차 (숫자). 명시되지 않았으면 0.
      "conditions": [
        {{ "action": "BUILT", "skill": "Payment_and_Settlement_System", "weight": 1.0, "is_mandatory": true }},
        {{ "action": "DESIGNED", "skill": "Data_Pipeline_Construction", "weight": 0.8, "is_mandatory": false }}
      ]
    }}
    
    * 규칙
    1. action은 [BUILT, DESIGNED, MANAGED, ANALYZED] 중 가장 적합한 것 1개를 선택하세요.
    2. skill은 아래 목록에 있는 단어 중 하나로만 맵핑하세요:
       [Payment_and_Settlement_System, Service_Planning, Product_Manager,
       Data_Pipeline_Construction, Data_Engineering, Data_Analysis,
       Backend, Frontend, Machine_Learning, MLOps, DevOps,
       Financial_Accounting, Corporate_Strategic_Planning, 사업개발_BD, 퍼포먼스마케팅,
       Treasury_Management, FX_Dealing, Corporate_Funding, IPO_Preparation_and_Execution,
       Recruiting_and_Talent_Acquisition, Organizational_Development, B2B영업, 물류_Logistics,
       Backend_Python, Backend_Java, Backend_Go, Backend_Node,
       Kubernetes, Infrastructure_and_Cloud, 보안_Security, FinTech,
       Natural_Language_Processing, 컴퓨터비전_CV, 추천시스템, Deep_Learning]
    3. is_mandatory는 "우대(preferred)", "경험자(plus)" 등의 뉘앙스면 false, 그 외 필수면 true로 설정하세요.
    4. weight는 가장 핵심 역량일수록 1.0에 가깝에, 덜 중요할수록 0.5 등으로 배정하세요.
    
    채용공고 텍스트:
    {jd_text}
    \"\"\"
    
    for attempt in range(3):
        try:
            response = model.generate_content(prompt)
            raw = response.text.replace('```json', '').replace('```', '').strip()
            parsed = json.loads(raw)
            logger.info(f"Successfully extracted {len(parsed.get('conditions',[]))} conditions and min_years: {parsed.get('min_years')}")
            
            # Save cache
            cache = {}
            if os.path.exists(JD_CACHE_FILE):
                with open(JD_CACHE_FILE, "r", encoding="utf-8") as f:
                    cache = json.load(f)
            cache[h] = parsed
            with open(JD_CACHE_FILE, "w", encoding="utf-8") as f:
                json.dump(cache, f, ensure_ascii=False, indent=2)
                
            return parsed
        except Exception as e:
            logger.error(f"Attempt {attempt+1} Error: {e}")
            time.sleep(1.5)
            
    return {"min_years": 0, "conditions": []}
"""

old_parse_pattern = r"def parse_jd_to_json\(jd_text:\s*str\)\s*->\s*dict:.*?(?=\ndef apply_downgrade_map\()"
jd_code = re.sub(old_parse_pattern, new_parse_jd_func + "\n", jd_code, flags=re.DOTALL)

with open("jd_compiler.py", "w", encoding="utf-8") as f:
    f.write(jd_code)

print("Batch & Cache Patch Complete!")
