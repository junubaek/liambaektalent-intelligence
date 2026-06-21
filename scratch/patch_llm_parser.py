# -*- coding: utf-8 -*-
"""
jd_compiler.py에 TTLCache + parse_jd_with_llm 추가,
api_search_v9에 preferred_companies boost + min_years 필터 통합
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')

INSERT_CODE = r'''
import hashlib
import time as _time_module

class TTLCache:
    """TTL(Time-To-Live) 기반 메모리 캐시 - 일정 시간 후 자동 만료"""
    def __init__(self, ttl_seconds: int = 3600):
        self._cache = {}
        self.ttl = ttl_seconds

    def get(self, key: str):
        if key not in self._cache:
            return None
        value, expire_at = self._cache[key]
        if _time_module.time() > expire_at:
            del self._cache[key]
            return None
        return value

    def set(self, key: str, value):
        self._cache[key] = (value, _time_module.time() + self.ttl)

    def clear(self):
        self._cache.clear()

_query_parse_cache = TTLCache(ttl_seconds=3600)

def parse_jd_with_llm(jd_text: str, openai_client) -> dict:
    """LLM 기반 쿼리 파서: preferred_companies, min_years, seniority 추출"""
    import json as _json
    cache_key = hashlib.md5(jd_text.encode()).hexdigest()
    cached = _query_parse_cache.get(cache_key)
    if cached:
        return cached

    system_prompt = (
        "You are a Korean talent search expert.\n"
        "Parse the job search query and extract structured information.\n"
        "Return ONLY a JSON object with these fields:\n"
        "- skills: list of canonical skill names (English, e.g. Backend, Machine_Learning, Finance)\n"
        "- min_years: integer (0 unless the query EXPLICITLY mentions years like '10년차 이상', '7년 경력')\n"
        "- max_years: integer (99 if not specified)\n"
        "- seniority: one of junior/mid/senior/executive or empty string\n"
        "- preferred_companies: list of company names mentioned (e.g. 카카오, 삼성전자, McKinsey)\n"
        "- keywords: list of other important keywords\n"
        "- sector: sector name (e.g. Eng_SW, Finance, Eng_AI, Strategy)\n"
        "- intent: brief description in Korean\n"
        "IMPORTANT: min_years must be 0 unless explicitly stated in the query.\n"
        "Do not infer min_years from seniority labels alone."
    )

    try:
        resp = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": jd_text}
            ],
            response_format={"type": "json_object"},
            temperature=0.0,
            max_tokens=400,
        )
        raw = resp.choices[0].message.content
        result = _json.loads(raw)
        result["_source"] = "llm"
        result["_cache_key"] = cache_key
        _query_parse_cache.set(cache_key, result)
        return result
    except Exception as e:
        logger.warning(f"[parse_jd_with_llm] LLM 파싱 실패: {e}")
        return {"skills": [], "min_years": 0, "max_years": 99, "seniority": "",
                "preferred_companies": [], "keywords": [], "sector": "", "intent": "",
                "_source": "fallback"}

'''

# Step 1: Insert TTLCache + parse_jd_with_llm before get_company_boost
TARGET_FILE = "jd_compiler.py"

with open(TARGET_FILE, encoding="utf-8") as f:
    content = f.read()

INSERT_MARKER = "def get_company_boost(company_name, conditions, conn):"
if INSERT_MARKER not in content:
    print("ERROR: marker 'get_company_boost' not found!")
    sys.exit(1)

if "class TTLCache" in content:
    print("TTLCache already present, skipping insert.")
else:
    idx = content.find(INSERT_MARKER)
    content = content[:idx] + INSERT_CODE + content[idx:]
    print(f"Inserted TTLCache + parse_jd_with_llm ({len(INSERT_CODE)} chars)")

# Step 2: Patch api_search_v9 Step 1 parsing block
OLD_STEP1 = """    # 1. Parse & Expand Query
    logger.info(f"DEBUG [V9] Step 1: Parsing query...")
    extracted = parse_jd_to_json(prompt)
    conds = extracted.get("conditions", [])"""

NEW_STEP1 = """    # 1. Parse & Expand Query
    logger.info(f"DEBUG [V9] Step 1: Parsing query...")
    with open(SECRETS_PATH, "r", encoding="utf-8") as _f_sec:
        _sec = json.load(_f_sec)
    _openai_client = client if 'client' in dir() else OpenAI(api_key=_sec.get("OPENAI_API_KEY"))
    # 규칙 기반 파서 (스킬 매핑 주담당)
    extracted = parse_jd_to_json(prompt)
    conds = extracted.get("conditions", [])
    min_years_rule = extracted.get("min_years", 0)
    # LLM 파서: preferred_companies + 명시적 min_years 보강
    _jd_llm = parse_jd_with_llm(prompt, _openai_client)
    preferred_companies = _jd_llm.get("preferred_companies", [])
    _min_years_llm = _jd_llm.get("min_years", 0)
    min_years = _min_years_llm if _min_years_llm > 0 else min_years_rule
    logger.info(f"[V9-LLM] preferred_companies={preferred_companies}, min_years={min_years}")"""

if OLD_STEP1 not in content:
    print("ERROR: Step 1 target block not found - check indentation!")
    # Try to debug
    lines = content.split("\n")
    for i, line in enumerate(lines):
        if "# 1. Parse" in line and "v9" not in line.lower():
            print(f"  Line {i+1}: {line}")
    sys.exit(1)

content = content.replace(OLD_STEP1, NEW_STEP1, 1)
print("Patched Step 1 parsing block")

# Step 3: Add company_boost precompute after conn.close() in api_search_v9
OLD_CONN_CLOSE = """    finally:
        conn.close()

    # Calculate accurate Graph (G) and Depth (D) score for every candidate in the pool"""

NEW_CONN_CLOSE = """    finally:
        conn.close()

    # Precompute preferred companies boost from raw_text
    company_boost_map = {}
    if preferred_companies:
        for _cid in combined_ids:
            _raw = raw_text_map.get(_cid, "")
            if _raw:
                _raw_lower = _raw.lower()
                for _co in preferred_companies:
                    if _co.lower() in _raw_lower:
                        company_boost_map[_cid] = company_boost_map.get(_cid, 0.0) + 0.04
                        break

    # Calculate accurate Graph (G) and Depth (D) score for every candidate in the pool"""

if OLD_CONN_CLOSE not in content:
    print("ERROR: conn.close() target block not found!")
    sys.exit(1)

content = content.replace(OLD_CONN_CLOSE, NEW_CONN_CLOSE, 1)
print("Patched company_boost precompute block")

# Step 4: Add seniority filter + company_boost in scoring loop
OLD_SCORING_LOOP = """    final_candidates = []
    for cid in combined_ids:
        norm_v = (v_scores.get(cid, 0.0) / max_v) if max_v > 0 else 0.0"""

NEW_SCORING_LOOP = """    final_candidates = []
    for cid in combined_ids:
        # min_years 경험 필터 (명시적 연차 요건이 있는 경우)
        if min_years > 0:
            _total_yrs = db_metadata_map.get(cid, {}).get("total_years", 0) or 0
            if _total_yrs < min_years:
                continue

        norm_v = (v_scores.get(cid, 0.0) / max_v) if max_v > 0 else 0.0"""

if OLD_SCORING_LOOP not in content:
    print("ERROR: scoring loop target block not found!")
    sys.exit(1)

content = content.replace(OLD_SCORING_LOOP, NEW_SCORING_LOOP, 1)
print("Patched scoring loop with min_years filter")

# Step 5: Add preferred company boost to final_score (after program_boost)
OLD_FINAL_SCORE = """        final_score = (norm_v * w_v) + (norm_g * w_g) + (norm_b * w_b) + (depth_score * w_d) + program_boost
        
        # [Signal 4] Company Intelligence Boost"""

NEW_FINAL_SCORE = """        final_score = (norm_v * w_v) + (norm_g * w_g) + (norm_b * w_b) + (depth_score * w_d) + program_boost
        # Preferred companies boost (from LLM extraction)
        final_score += company_boost_map.get(cid, 0.0)
        
        # [Signal 4] Company Intelligence Boost"""

if OLD_FINAL_SCORE not in content:
    print("ERROR: final_score target block not found!")
    sys.exit(1)

content = content.replace(OLD_FINAL_SCORE, NEW_FINAL_SCORE, 1)
print("Patched preferred companies boost into final_score")

# Write back
with open(TARGET_FILE, "w", encoding="utf-8") as f:
    f.write(content)

print("\nAll patches applied successfully!")
print(f"New file size: {len(content)} chars")
