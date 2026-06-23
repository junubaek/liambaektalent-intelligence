from ontology_graph import UNIFIED_GRAVITY_FIELD, SENIOR_EXPANDED_SYNERGY
import sqlite3, os, json, uuid, re

from openai import OpenAI

from connectors.pinecone_api import PineconeClient

from vector_fallback import get_closest_node

from openai import OpenAI



# Robust path for secrets.json
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
SECRETS_PATH = os.path.join(ROOT_DIR, "secrets.json")

def _get_secret(key):
    val = os.environ.get(key)
    if val: return val
    try:
        with open(SECRETS_PATH, "r", encoding="utf-8") as f:
            return json.load(f).get(key, "")
    except Exception:
        return ""

secret_data = {
    "OPENAI_API_KEY": _get_secret("OPENAI_API_KEY"),
    "PINECONE_HOST": _get_secret("PINECONE_HOST"),
    "PINECONE_API_KEY": _get_secret("PINECONE_API_KEY")
}

openai_client = OpenAI(api_key=secret_data.get("OPENAI_API_KEY", ""))

pc_host = secret_data.get("PINECONE_HOST", "").rstrip("/")

if not pc_host.startswith("https://"):

    pc_host = f"https://{pc_host}"

pc_client = PineconeClient(secret_data.get("PINECONE_API_KEY", ""), pc_host)



SESSION_STORE = {}

import hashlib

import logging

from typing import List, Dict

from pydantic import BaseModel

from google import genai

import numpy as np

from sklearn.feature_extraction.text import TfidfVectorizer

from sklearn.metrics.pairwise import cosine_similarity

from collections import defaultdict

import math



from neo4j import GraphDatabase

from connectors.pinecone_api import PineconeClient

from connectors.openai_api import OpenAIClient

from ontology_graph import CANONICAL_MAP

from vector_fallback import get_closest_node



# 🌌 [신규 적용] V8.5 통합 중력장 사전 (UNIFIED_GRAVITY_FIELD)





# 🛡️ 제너럴리스트 보호 노드 (한국 스타트업 C-Level 및 리더급 확장)

ACTION_WEIGHTS = {
    'BUILT': 2.0,
    'DESIGNED': 1.9,
    'CLOSED': 1.4,
    'LED': 1.4,
    'MIGRATED': 1.7,
    'DEPLOYED': 1.6,
    'OPTIMIZED': 1.5,
    'RESOLVED': 1.5,
    'ANALYZED': 1.4,
    'INTEGRATED': 1.4,
    'LAUNCHED': 1.4,
    'GREW': 1.4,
    'PLANNED': 1.3,
    'DRAFTED': 1.3,
    'EXECUTED': 1.3,
    'NEGOTIATED': 1.3,
    'MANAGED': 1.0,
    'OPERATED': 1.0,
    'SUPPORTED': 1.0,
    'USED': 0.3
}

EXECUTIVE_NODES = {

    "Chief_Executive_Officer",

    "Chief_Operating_Officer",

    "Chief_Financial_Officer", 

    "Chief_Compliance_Officer", 

    "Chief_Revenue_Officer",

    "Chief_Technology_Officer",

    "Chief_Marketing_Officer",

    "Vice_President",

    "General_Manager",

    "Head_of",

    "Platform_Product_Owner", 

    "Product_Manager", 

    "Product_Owner", 

    "New_Biz_Incubation"

}




REPEL_MULTIPLIER = {
    "JUNIOR":  1.0,   # 풀 척력 — 직무 경계 엄격
    "MIDDLE":  0.5,   # 중간 — 약간의 유연성
    "SENIOR":  0.15,  # 거의 무력화 — 폭넓은 경험 인정
    "All":     0.7,   # 기본값
}

def get_seniority_label(total_years):
    if not total_years or total_years == 0:
        return '미상'
    elif total_years >= 10:
        return 'SENIOR'
    elif total_years >= 5:
        return 'MIDDLE'
    else:
        return 'JUNIOR'


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


import logging
logger = logging.getLogger(__name__)

class OntologyVectorIndex:
    """
    온톨로지 노드 벡터 인덱스 (Ontology Vector Index)
    - 노드명 단독 임베딩 (1515노드 × 1536차원)
    - LLM이 추출한 스킬명을 임베딩 → 코사인 유사도로 온톨로지 노드 탐색
    - exact match 미스 케이스 보완
    """
    def __init__(self, pkl_path='ontology_vectors.pkl'):
        self._nodes = []
        self._matrix = None
        self._skill_cache = {}  # skill_text → embedding 캐시
        try:
            import pickle, numpy as _np
            if not os.path.exists(pkl_path):
                logger.warning(f"[OntologyVectorIndex] {pkl_path} not found. Disabled.")
                return
            with open(pkl_path, 'rb') as f:
                data = pickle.load(f)
            self._nodes = [item['node'] for item in data]
            matrix = _np.array([item['vector'] for item in data])
            # 행별 정규화 (코사인 유사도 = 내적)
            norms = _np.linalg.norm(matrix, axis=1, keepdims=True)
            norms[norms == 0] = 1.0
            self._matrix = matrix / norms
            logger.info(f"[OntologyVectorIndex] Loaded {len(self._nodes)} nodes, {self._matrix.shape[1]}dim")
        except Exception as e:
            logger.warning(f"[OntologyVectorIndex] Init failed: {e}")

    def search(self, skill_text: str, openai_client, threshold=0.80, top_k=5) -> list:
        """스킬명을 임베딩해서 유사한 온톨로지 노드 반환"""
        if self._matrix is None or not skill_text:
            return []
        import numpy as _np
        try:
            # 캐시 확인
            if skill_text in self._skill_cache:
                q_vec = self._skill_cache[skill_text]
            else:
                resp = openai_client.embeddings.create(
                    input=[skill_text], model="text-embedding-3-small"
                )
                q_arr = _np.array(resp.data[0].embedding)
                q_vec = q_arr / (_np.linalg.norm(q_arr) or 1.0)
                self._skill_cache[skill_text] = q_vec
            sims = self._matrix @ q_vec
            top_idx = _np.argsort(-sims)
            return [(self._nodes[i], float(sims[i]))
                    for i in top_idx if float(sims[i]) >= threshold][:top_k]
        except Exception as e:
            logger.warning(f"[OntologyVectorIndex] search failed: {e}")
            return []

_ontology_index = OntologyVectorIndex()

def get_company_boost(company_name, conditions, conn):
    try:
        import json
        # 회사명 정규화 (간단 버전)
        normalized = company_name.strip() if company_name else ''
        for suffix in ['(주)', '㈜', '(유)', '주식회사']:
            normalized = normalized.replace(suffix, '').strip()
        
        cur = conn.cursor()
        cur.execute('''
            SELECT scale, sector, inferred_skills, traffic_scale, major_events
            FROM company_intelligence
            WHERE normalized_name = ?
            OR company_name = ?
        ''', (normalized, company_name))
        row = cur.fetchone()
        if not row:
            return 0.0
        
        scale, sector, skills_json, traffic, events_json = row
        skills = json.loads(skills_json or '{}')
        
        boost = 0.0
        skill_names = [c.get('skill','') for c in conditions]
        
        # 대용량 트래픽 관련 검색 + 대규모 트래픽 회사
        traffic_nodes = {'Back-end_Development', 'Kubernetes', 'DevOps', 
                        'Distributed_Systems', 'Cloud_Infrastructure', 'MSA'}
        if traffic in ('대규모', '초대규모') and traffic_nodes & set(skill_names):
            boost += 0.03
        
        # 금융 관련 검색 + 금융/컨설팅 회사
        finance_nodes = {'Treasury_Management', 'Corporate_Finance', 
                        'Financial_Management', 'M_and_A', 'Valuation'}
        if sector in ('금융', '컨설팅') and finance_nodes & set(skill_names):
            boost += 0.03
        
        # 글로벌 대기업 보너스
        if scale == '글로벌대기업':
            boost += 0.01
        
        return min(boost, 0.05)
    except:
        return 0.0

def get_effective_gravity(node, seniority):
    field = UNIFIED_GRAVITY_FIELD.get(node, {}).copy()
    
    # SENIOR일 때 시너지 노드 확장
    if seniority == "SENIOR":
        expanded = SENIOR_EXPANDED_SYNERGY.get(node, [])
        extra = {n: 0.4 for n in expanded}  # 확장 시너지 가중치 0.4
        existing = field.get("synergy_attracts", {})
        field["synergy_attracts"] = {**existing, **extra}
    
    return field

def calc_achievement_density(raw_text):
    if not raw_text:
        return 0.0
    import re
    # [Core] 실무 수치 패턴 (1.0 가중치)
    core_patterns = [
        r'\d+%', r'\d+억', r'\d+만', r'\d+명', r'\d+개', r'\d+년'
    ]
    # [Tech] 기술 깊이 신호 (0.5 가중치)
    tech_patterns = [
        r'특허', r'논문', r'제1저자', r'SCI', r'수상', r'\d+건'
    ]
    
    core_count = sum(len(re.findall(p, raw_text)) for p in core_patterns)
    tech_count = sum(len(re.findall(p, raw_text)) for p in tech_patterns)
    
    # 가중 합산
    weighted_count = core_count + (tech_count * 0.5)
    
    # 텍스트 1000자당 밀도
    density = weighted_count / (max(len(raw_text), 1) / 1000)
    # 0~1 정규화 (5개/1000자 = 만점 기준)
    return min(density / 5.0, 1.0)

def calc_gravity_score(candidate_nodes, query_nodes, seniority="All"):
    
    repel_mult = REPEL_MULTIPLIER.get(seniority, 0.7)
    
    score = 0
    for node in query_nodes:
        field = get_effective_gravity(node, seniority)
        
        # 핵력 — seniority 무관하게 풀 적용
        core = field.get("core_attracts", {})
        for cnode, weight in core.items():
            if cnode in candidate_nodes:
                score += weight * 2.0  # core 가산
        
        # 시너지
        synergy = field.get("synergy_attracts", {})
        for snode, weight in synergy.items():
            if snode in candidate_nodes:
                score += weight
        
        # 척력 — seniority에 따라 감쇠
        repels = field.get("repels", {})
        for rnode, weight in repels.items():
            if rnode in candidate_nodes:
                score += weight * repel_mult  # 음수 × 배수
    
    return score


def calculate_gravity_fusion_score(candidate_edges, conds, is_category_search=False):
    if not conds or not isinstance(candidate_edges, list):
        return 0.0

    jd_target_skills = [c.get('skill', '') for c in conds if c.get('skill')]
    DEPTH_MULTIPLIER = {1: 1.0, 2: 1.1, 3: 1.2, 4: 1.3}

    matched_skill_actions = {}
    for edge in candidate_edges:
        if isinstance(edge, dict):
            skill = edge.get('skill', '')
            action = edge.get('action', 'MANAGED')
            last_used = edge.get('last_used_year')
        else:
            skill = edge
            action = "MANAGED"
            last_used = None
            
        if skill in jd_target_skills:
            weight = ACTION_WEIGHTS.get(action, 1.0)
            if last_used is not None:
                try:
                    last_used_val = float(last_used)
                    decay = max(0.5, 1.0 - 0.10 * (2025 - last_used_val))
                    weight *= decay
                except (ValueError, TypeError):
                    pass
            if skill not in matched_skill_actions:
                matched_skill_actions[skill] = []
            matched_skill_actions[skill].append(weight)

    matched_score = 0
    for skill, weights in matched_skill_actions.items():
        max_weight = max(weights)
        depth = min(len(weights), 4)
        depth_mult = DEPTH_MULTIPLIER[depth]
        matched_score += max_weight * depth_mult

    return matched_score

logging.basicConfig(level=logging.INFO)



GLOBAL_GEMINI_CALL_COUNT = 0



# 역할 노드 판별용 목록 (CANONICAL_MAP의 역할 관련 노드들)

ROLE_NODES = {

    "Product_Manager", "Product_Owner", "Project_Manager",

    "Financial_Planning_and_Analysis", "Treasury_Management",

    "IPO_Preparation_and_Execution", "Corporate_Strategic_Planning",

    "Backend_Architecture", "Data_Engineering", "Data_Analysis",

    "Machine_Learning", "Recruiting_and_Talent_Acquisition",

    "Organizational_Development", "Chief_Financial_Officer",

    "HR_Strategic_Planning", "Marketing_Leadership",

}





def inject_node_affinity(conditions: list) -> list:

    if not conditions:

        return conditions



    existing_skills = {c["skill"] for c in conditions}



    detected_roles = [

        c["skill"] for c in conditions

        if c["skill"] in UNIFIED_GRAVITY_FIELD

    ]



    if not detected_roles:

        return conditions



    affinity_added = []



    for role in detected_roles:

        field = UNIFIED_GRAVITY_FIELD[role]

        # Use core and synergy attracts

        attracts = {}

        if "core_attracts" in field:

            attracts.update(field["core_attracts"])

        if "synergy_attracts" in field:

            attracts.update(field["synergy_attracts"])



        for affinity_skill, weight in attracts.items():

            if affinity_skill not in existing_skills:

                affinity_added.append({

                    "action": "MANAGED",

                    "skill": affinity_skill,

                    "weight": weight * (1.4 / 1.8), # Synergy Multiplier applied

                    "is_mandatory": False,

                    "source": "auto_affinity"

                })

                existing_skills.add(affinity_skill)



    if affinity_added:

        import logging

        logger = logging.getLogger(__name__)

        logger.info(

            f"[Affinity Injected] {len(affinity_added)}개 조건 자동 추가: "

            f"{[a['skill'] for a in affinity_added]}"

        )



    return conditions + affinity_added





from backend.search_engine_v5 import notion_query_raw

from connectors.pinecone_api import PineconeClient

from connectors.openai_api import OpenAIClient



# Logger setup

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

logger = logging.getLogger(__name__)



# --- 1. Load Secrets and Setup Gemini ---

GENAI_KEY = os.environ.get("GEMINI_API_KEY")
if not GENAI_KEY:
    try:
        with open(SECRETS_PATH, "r", encoding="utf-8") as f:
            GENAI_KEY = json.load(f).get("GEMINI_API_KEY", "PLEASE_SET_KEY")
    except Exception as e:
        logger.warning(f"{SECRETS_PATH} not found or invalid format.")
        GENAI_KEY = "PLEASE_SET_KEY"



client = genai.Client(api_key=GENAI_KEY)

MODEL_ID = 'gemini-2.5-flash'



def get_history_bonus_scores(jd_text: str, top_k: int = 50) -> Dict[str, Dict]:

    try:

        secret_data = {
            "PINECONE_HOST": _get_secret("PINECONE_HOST"),
            "PINECONE_API_KEY": _get_secret("PINECONE_API_KEY"),
            "OPENAI_API_KEY": _get_secret("OPENAI_API_KEY")
        }

            

        pc_host = secret_data.get("PINECONE_HOST", "").rstrip("/")

        if not pc_host.startswith("https://"):

            pc_host = f"https://{pc_host}"

            

        pc = PineconeClient(secret_data.get("PINECONE_API_KEY", ""), pc_host)

        openai = OpenAIClient(secret_data.get("OPENAI_API_KEY", ""))

        

        jd_vector = openai.embed_content(jd_text)

        if not jd_vector:

            return {}

            

        res = pc.query(jd_vector, top_k=top_k, namespace="history_v4_2")

        if not res or "matches" not in res:

            return {}

            

        bonus_map = {}

        for match in res["matches"]:

            if match.get("score", 0) < 0.6:

                continue

                

            meta = match.get("metadata", {})

            name = meta.get("name", "")

            status = meta.get("status", "")

            drop_reason = meta.get("drop_reason", "")

            

            if not name or name in bonus_map:

                continue

                

            score = 0

            msg = ""

            if status == "최종합격":

                score = 0.3

                msg = "[+ 유사 포지션 합격 이력]"

            elif status in ["서류합격", "면접합격"]:

                score = 0.2

                msg = "[+ 유사 포지션 합격 이력]"

            elif drop_reason == "미스매치":

                score = -0.3

                msg = "[- 유사 포지션 미스매치 이력]"

            elif drop_reason == "역량부족":

                score = -0.1

                msg = "[- 유사 포지션 역량부족 이력]"

                

            if score != 0:

                bonus_map[name] = {"score": score, "msg": msg}

                

        return bonus_map

    except Exception as e:

        logger.error(f"Failed to fetch history bonus: {e}")

        return {}





def parse_jd_to_json(jd_text: str) -> Dict:
    """
    자연어 JD를 입력받아, 필수/우대 구조의 화학식 JSON 및 최소 연차 정보를 반환합니다.
    """
    global GLOBAL_GEMINI_CALL_COUNT
    import re
    
    # 1000자 초과 시 핵심만 남기고 단축 (토큰 및 속도 절감)
    if len(jd_text) > 1000:
        jd_text = jd_text[:1000]

    # [Native] 1. 연차 추출 정규식

    min_years = 0

    years_matches = re.findall(r"(\d+)\s*년\s*(?:차|이상|경력|차이상)", jd_text)

    if years_matches:

        min_years = min(int(y) for y in years_matches)

        

    # [Native] 2. 딕셔너리 직접 조회

    lower_jd = jd_text.lower()

    matched_nodes = []

    seen_nodes = set()

    # [Patch] 카테고리 매칭 처리 (Step 5-B) + Category Flag
    from ontology_graph import SKILL_CATEGORIES
    is_category_search = False
    for cat_name, cat_skills in SKILL_CATEGORIES.items():
        if lower_jd.strip() == cat_name.lower():
            is_category_search = True
            for s in cat_skills:
                if s not in seen_nodes:
                    seen_nodes.add(s)
                    matched_nodes.append((s, cat_name.lower()))


    


    # 가장 긴 단어부터 매칭(부분충돌 방지)
    sorted_keys = sorted(CANONICAL_MAP.keys(), key=len, reverse=True)
    canonical_values = sorted(list(set(CANONICAL_MAP.values())), key=len, reverse=True)

    for k in sorted_keys:
        k_lower = k.lower()
        if k_lower in lower_jd:
            if re.search(r'[a-z]', k_lower):
                pattern = r'(?<![a-z0-9])' + re.escape(k_lower) + r'(?![a-z0-9])'
                if not re.search(pattern, lower_jd):
                    continue
            v = CANONICAL_MAP[k]
            if v not in seen_nodes:
                seen_nodes.add(v)
                matched_nodes.append((v, k_lower))

    # [Patch] Value(노드명) 직접 매칭 추가 (v7 대응)
    for val in canonical_values:
        val_lower = val.lower()
        for p in [val_lower, val_lower.replace('_', ' ')]:
            if p in lower_jd:
                if re.search(r'[a-z]', p):
                    p_regex = r'(?<![a-z0-9])' + re.escape(p) + r'(?![a-z0-9])'
                    if not re.search(p_regex, lower_jd):
                        continue
                if val not in seen_nodes:
                    seen_nodes.add(val)
                    matched_nodes.append((val, p))
                    break

                    

    # [Patch] CANONICAL_MAP에 없는 자유 영문 단어 추출
    stopwords = {"the", "and", "for", "with", "using", "based", "to", "of", "in", "a", "an", "on", "as", "is", "are", "or", "by", "all", "any", "not"}
    free_words = []
    for word in re.findall(r'[A-Za-z][A-Za-z0-9_]+', jd_text):
        if len(word) >= 2 and word.lower() not in stopwords:
            free_words.append(word)
    free_words = list(dict.fromkeys(free_words))
    
    if matched_nodes or free_words:
        conditions = []
        mandatory_assigned = False
        CONTEXT_PATTERN = r'(?:[\s/가-힣A-Za-z0-9]{0,8})?(?:를\s*)?(?:을\s*)?(?:대비|준비|예정|앞두고)'
        
        for node, k_lower in matched_nodes:
            action = "MANAGED"
            pattern = re.escape(k_lower) + CONTEXT_PATTERN
            is_background = bool(re.search(pattern, lower_jd))
            conditions.append({
                "action": action,
                "skill": node,
                "weight": 1.0,
                "is_mandatory": not is_background, 
                "source": "native_dict"
            })
            
        for w in free_words:
            if not any(w.lower() in c['skill'].lower() for c in conditions):
                conditions.append({
                    "action": "MANAGED",
                    "skill": w,
                    "weight": 1.0,
                    "is_mandatory": True, 
                    "source": "freeform"
                })


            

        # 가중치 높은 순으로 정렬 (웨이트가 같다면 원래 순서)

        conditions.sort(key=lambda x: x['weight'], reverse=True)



        from neo4j import GraphDatabase

        def has_candidates(skill_name):

            try:

                import os
                n_uri = _get_secret('NEO4J_URI')
                n_user = _get_secret('NEO4J_USERNAME')
                n_pw = _get_secret('NEO4J_PASSWORD')
                driver = GraphDatabase.driver(n_uri, auth=(n_user, n_pw))

                with driver.session() as s:

                    cnt = s.run(

                        'MATCH (c:Candidate)-[]->(s:Skill {name:$name}) '

                        'RETURN count(c) as cnt',

                        name=skill_name

                    ).single()['cnt']

                driver.close()

                return cnt >= 5

            except Exception as e:

                return False



        # Mandatory 후보 중 DB에 있는 것만 필터

        valid_mandatory = [c for c in conditions if has_candidates(c['skill'])]



        # 상위 2개만 Mandatory, 나머지 Optional

        mandatory_count = 0

        for cond in conditions:

            if cond in valid_mandatory:

                if mandatory_count >= 2:

                    cond['is_mandatory'] = False

                else:

                    cond['is_mandatory'] = True

                    mandatory_count += 1

            else:

                cond['is_mandatory'] = False

            

        logger.info(f"[Native Map Hit] Extracted {len(conditions)} conditions without Gemini. Min years: {min_years}")

        return {"min_years": min_years, "conditions": conditions, "is_category_search": is_category_search}



    logger.info("No native map hits (L1 Fail). Trying L2 Vector Fallback...")

    # GLOBAL_GEMINI_CALL_COUNT += 1 (Using fallback instead of full Gemini Flash 2.5 API here)

    

    fallback_node = get_closest_node(jd_text, threshold=0.45)

    

    if fallback_node:

        conditions = [{

            "action": "MANAGED",

            "skill": fallback_node,

            "weight": 1.0,

            "is_mandatory": True,

            "source": "vector_fallback"

        }]

        logger.info(f"Fallback Routing Success: {fallback_node}")

        return {"min_years": min_years, "conditions": conditions, "is_category_search": is_category_search}

    

    # L1, L2 모두 실패

    return {"min_years": min_years, "conditions": [], "error": "검색어를 더 구체적으로 입력해 주세요.", "is_category_search": False}





def expand_jd_keywords(jd_text: str) -> str:

    """

    JD의 핵심 키워드를 추출하고 동의어로 확장하여 TF-IDF 검색 시 어휘 불일치(Vocabulary Mismatch) 문제를 완화합니다.

    """

    logger.info("Expanding JD keywords via native CANONICAL_MAP synonyms...")

    

    inverse_map = {}

    for k, v in CANONICAL_MAP.items():

        if v not in inverse_map:

            inverse_map[v] = set()

        inverse_map[v].add(k)

        

    lower_jd = jd_text.lower()

    matched_nodes = set()

    

    for k, v in CANONICAL_MAP.items():

        if k.lower() in lower_jd:

            matched_nodes.add(v)

            

    expanded_words_list = []

    for node in matched_nodes:

        if node in inverse_map:

            expanded_words_list.extend(list(inverse_map[node]))

            

    expanded_words = ", ".join(set(expanded_words_list))

    logger.info(f"Expanded Keywords (Native): {expanded_words}")

    

    # 전략적 키워드 하드코딩 부스팅 (자금/Treasury 관련)

    lower_jd = jd_text.lower()

    if any(k in lower_jd for k in ["자금", "treasury", "ipo", "펀딩"]):

        boost_kws = ["자금", "Treasury", "Cash", "FX", "환리스크"]

        # TF-IDF 가중치를 높이기 위해 여러 번 반복 주입

        boost_str = " ".join(boost_kws) * 5

        expanded_words += " " + boost_str

        logger.info(f"Applying manual Treasury keyword boost to TF-IDF corpus.")

    

    # 원본 JD에 확장 키워드를 붙여서 반환 (가중치 상승 효과)

    return jd_text + " " + expanded_words



def get_candidates_from_cache() -> List[Dict]:

    """

    V8.5 SQLAlchemy ORM DB(candidates.db) 에서만 데이터를 읽습니다.

    Notion API 의존성이 제로입니다.

    """

    from app.database import SessionLocal

    from app.models import Candidate, ParsingCache

    

    db = SessionLocal()

    try:

        # Include json cache to fallback missing properties

        import json, os

        json_cache = {}
        json_cache_by_id = {}

        cache_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "candidates_cache_jd.json")

        if os.path.exists(cache_path):

            with open(cache_path, "r", encoding="utf-8") as f:

                try: old_data = json.load(f)

                except: old_data = []

                for d in old_data:

                    if "id" in d and d["id"]:
                        json_cache_by_id[str(d["id"])] = d
                        json_cache_by_id[str(d["id"]).replace("-", "")] = d
                    if "name_kr" in d: json_cache[d["name_kr"]] = d

                    elif "name" in d: json_cache[d["name"]] = d

                    

        rows = db.query(Candidate).outerjoin(ParsingCache).filter(Candidate.is_duplicate == 0).all()

        candidates = []

        for c in rows:

            cache_ext = c.parsing_cache.parsed_dict if c.parsing_cache else {}

            fb_data = json_cache_by_id.get(str(c.id)) or json_cache_by_id.get(str(c.id).replace("-", "")) or json_cache.get(c.name_kr) or {}
            if not fb_data and c.name_kr:
                c_clean = c.name_kr.replace(" ", "")
                for k, v in json_cache.items():
                    if c_clean in k.replace(" ", ""):
                        fb_data = v
                        break

            

            raw_t = c.raw_text if c.raw_text else fb_data.get("summary", "")

            if not raw_t or len(raw_t) < 100:

                continue

                

            # 1. DB careers_json 최우선 반영 여부 (새로 구운 캐시를 최우선으로)

            db_careers = json.loads(c.careers_json) if getattr(c, "careers_json", None) else []

            careers_list = fb_data.get("parsed_career_json") or db_careers or cache_ext.get("careers", [])

            c_list = careers_list            

            # Robust company extraction

            current_comp = "미상"

            if c_list and isinstance(c_list, list) and len(c_list) > 0 and isinstance(c_list[0], dict):

                current_comp = c_list[0].get("company") or "미상"

            

            if current_comp == "미상" or current_comp == "":

                current_comp = fb_data.get("current_company") or "미상"

                if current_comp == "": current_comp = "미상"

            

            seniority_val = cache_ext.get("seniority", "")

            if not seniority_val or "확인" in seniority_val or "미상" in seniority_val:

                seniority_val = fb_data.get("seniority", "")

                

            if not seniority_val or "확인" in seniority_val or "미상" in seniority_val:

                import re

                from datetime import datetime

                calc_years = 0

                for cr in c_list:

                    if not isinstance(cr, dict): continue

                    pstr = cr.get("period", "")

                    if not pstr: continue

                    yrs = re.findall(r'(\d{4})', str(pstr))

                    if len(yrs) >= 2:

                        calc_years += max(0, int(yrs[-1]) - int(yrs[0]))

                    elif len(yrs) == 1 and ('현재' in str(pstr) or '재직' in str(pstr)):

                        calc_years += max(0, datetime.now().year - int(yrs[0]))

                        

                if calc_years >= 10: seniority_val = "Senior"

                elif calc_years >= 5: seniority_val = "Middle"

                elif calc_years > 0: seniority_val = "Junior"

                else: seniority_val = "Senior" # Defaults to Senior usually based on repo history



            prof_sum = cache_ext.get("profile_summary", "") or fb_data.get("profile_summary", "")
            if not prof_sum:
                prof_sum = ""



            candidates.append({

                "id": c.id,

                "name": c.name_kr,

                "name_kr": c.name_kr,

                "email": c.email,

                "phone": c.phone,

                "summary": raw_t,

                "profile_summary": prof_sum,

                "seniority": seniority_val,

                "current_company": current_comp,

                "main_sectors": cache_ext.get("main_sectors", []),

                "careers": careers_list,

                # To maintain compatibility with prior scripts that look for parsed_career_json mappings

                "parsed_career_json": careers_list,

                "birth_year": c.birth_year,

                "education_json": json.loads(c.education_json) if getattr(c, "education_json", None) else [],
                "notion_url": fb_data.get("notion_url", "#")
            })
            
        # Optional: Load Google Drive Maps if available
        import os
        drive_map = {}
        drive_map_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "drive_links_map.json")
        if os.path.exists(drive_map_path):
            with open(drive_map_path, "r", encoding="utf-8") as f:
                try: drive_map = json.load(f)
                except: pass
        for c in candidates:
            c["google_drive_url"] = drive_map.get(str(c["id"]).replace("-", ""), "")

        return candidates

    finally:

        db.close()





import math



def get_pinecone_scores(query_text: str, top_k: int = 200) -> dict:

    """

    Pinecone에서 query에 대한 유사도 벡터를 검색하여 {candidate_id: max_score} 딕셔너리를 반환.

    """

    try:

        if not pc_client.api_key or not openai_client.api_key:

            return {}

            

        emb_res = openai_client.embeddings.create(

            model="text-embedding-3-small",

            input=[query_text]

        )

        vec = emb_res.data[0].embedding

        

        pc_res = pc_client.query(vector=vec, top_k=top_k, namespace="resume_vectors")

        

        scores = {}

        if pc_res and "matches" in pc_res:

            for match in pc_res["matches"]:

                c_id = match.get("metadata", {}).get("candidate_id")

                score = match.get("score", 0.0)

                if c_id and (c_id not in scores or score > scores[c_id]):

                    scores[c_id] = score

        return scores

    except Exception as e:

        logger.error(f"[Pinecone API Error] {e}")

def get_bm25_top(query_text, top_k=100):
    """
    BM25 인덱스에서 검색하여 {candidate_id: score} 딕셔너리 반환
    """
    import os, pickle, re
    index_path = 'bm25_index.pkl'
    if not os.path.exists(index_path):
        return {}
    
    with open(index_path, 'rb') as f:
        data = pickle.load(f)
        bm25 = data['bm25']
        ids = data['ids']
    
    def tokenize(text):
        tokens = re.findall(r'[가-힣]{2,}|[a-zA-Z]{2,}|\d+', text or '')
        return [t.lower() for t in tokens]
    
    tokenized_query = tokenize(query_text)
    scores = bm25.get_scores(tokenized_query)
    
    # 0.0 ~ 1.0 정규화 (상위 점수 기준)
    max_s = max(scores) if len(scores) > 0 and max(scores) > 0 else 1.0
    
    # Top K 추출
    import numpy as np
    top_indices = np.argsort(scores)[::-1][:top_k]
    
    res = {}
    for idx in top_indices:
        s = scores[idx]
        if s > 0:
            res[str(ids[idx])] = s / max_s
    return res


def deduplicate_conditions(conds: List[Dict]) -> List[Dict]:

    DOWNGRADE_MAP = {

        "자금_Treasury": "Treasury_Management",

        "IPO_Preparation_and_Execution": "Corporate_Strategic_Planning",

        "Corporate_Funding": "Treasury_Management",

        "Supply_Chain_Management": "SCM",

        "물류_Logistics": "SCM"

    }

    

    for c in conds:

        original = c['skill']

        if original in DOWNGRADE_MAP:

            c['skill'] = DOWNGRADE_MAP[original]

            if original == "자금_Treasury":

                c['is_mandatory'] = True

                

    unique_conds = []

    seen = set()

    for c in conds:

        if c['skill'] not in seen:

            unique_conds.append(c)

            seen.add(c['skill'])

        else:

            # 병합 시 필수 조건 유실 방지

            for existing in unique_conds:

                if existing['skill'] == c['skill'] and c.get('is_mandatory'):
                    existing['is_mandatory'] = True
    return unique_conds

def apply_downgrade_map(conds: list) -> list:
    DOWNGRADE_MAP = {
        "자금_Treasury": "Treasury_Management",
        "IPO_Preparation_and_Execution": "Corporate_Strategic_Planning",
        "Corporate_Funding": "Treasury_Management",
        "Supply_Chain_Management": "SCM",
        "물류_Logistics": "SCM"
    }
    
    for c in conds:
        original = c['skill']
        if original in DOWNGRADE_MAP:
            c['skill'] = DOWNGRADE_MAP[original]
            if original == "자금_Treasury":
                c['is_mandatory'] = True
                
    unique_conds = []
    seen = set()
    for c in conds:
        if c['skill'] not in seen:
            unique_conds.append(c)
            seen.add(c['skill'])
        else:
            # 병합 시 필수 조건 유실 방지
            for existing in unique_conds:
                if existing['skill'] == c['skill'] and c.get('is_mandatory'):
                    existing['is_mandatory'] = True
    return unique_conds





def prefilter_candidates(jd_text: str, num_candidates: int = 300, extracted_conditions: List[Dict] = None) -> List[str]:
    """
    [긴급 수정] 무한 루프 방지를 위해 다단계 탐색 제거.
    가장 가벼운 1-Hop 직접 매칭만 수행 후, 부족하면 바로 TF-IDF Fallback 가동!
    """
    top_names = []
    
    if not extracted_conditions:
        logger.warning("[Reverse Funnel] No extracted conditions. Returning empty list.")
        return top_names

    target_nodes = [c["skill"].lower() for c in extracted_conditions]
    logger.info(f"[Reverse Funnel] Querying Neo4j for candidates linked to nodes: {target_nodes} (1-Hop)")
    
    from neo4j import GraphDatabase
    try:
        import os
        n_uri = _get_secret('NEO4J_URI')
        n_user = _get_secret('NEO4J_USERNAME')
        n_pw = _get_secret('NEO4J_PASSWORD')
        driver = GraphDatabase.driver(n_uri, auth=(n_user, n_pw))
        with driver.session() as session:
            # 1. 초경량 1-Hop 탐색 쿼리 (0.01초 보장)
            cypher_query = """
            MATCH (c:Candidate)-[r:BUILT|DESIGNED|MANAGED|ANALYZED|SUPPORTED|NEGOTIATED|GREW|LAUNCHED|LED|OPTIMIZED|PLANNED|EXECUTED|MIGRATED|DEPLOYED|RESOLVED|CLOSED|DRAFTED]->(s:Skill)
            WHERE toLower(s.name) IN $skills
            RETURN DISTINCT c.name_kr AS name, count(DISTINCT s) AS match_count
            ORDER BY match_count DESC
            LIMIT $limit
            """
            res = session.run(cypher_query, skills=target_nodes, limit=num_candidates)
            top_names = [{'name': rec["name"], 'graph_score': rec["match_count"], 'vector_score': 0.0} for rec in res]
            logger.info(f"[Reverse Funnel] Extracted {len(top_names)} candidates forcibly from graph as primary funnel.")
    except Exception as e:
        logger.error(f"[Reverse Funnel] Neo4j 쿼리 실패: {e}")
    finally:
        if 'driver' in locals(): driver.close()

    # 2. 안전망 (Fallback) 가동: Graph 0명일 때만 SQLite LIKE 검색
    if len(top_names) == 0:
        logger.warning(f"⚠️ Graph 검색 결과 0명. SQLite 원문 단순 LIKE 검색 Fallback 즉시 가동...")
        query_words = []
        if extracted_conditions:
            for c in extracted_conditions:
                if c.get("skill"):
                    # 단어가 여러 개인 경우 (예: "vLLM PyTorch") 쪼개서 넣기
                    words = c["skill"].lower().split()
                    query_words.extend(words)
        else:
            query_words = jd_text.lower().split()
            
        import sqlite3
        try:
            conn = sqlite3.connect(os.environ.get('DB_PATH', 'candidates.db'))
            c = conn.cursor()
            
            # AND 검색
            where_clauses = []
            params = []
            for word in query_words:
                where_clauses.append("LOWER(raw_text) LIKE ?")
                params.append(f"%{word}%")
            
            if where_clauses:
                query = f"SELECT name_kr FROM candidates WHERE {' AND '.join(where_clauses)} LIMIT {num_candidates}"
                c.execute(query, params)
                fallback_rows = c.fetchall()
                
                # OR 검색 (AND 검색 결과가 0명이고 키워드가 여러개일 경우)
                if len(fallback_rows) == 0 and len(query_words) > 1:
                    logger.warning("SQLite AND 검색 0명. OR 조건으로 재검색합니다.")
                    where_clauses_or = []
                    params_or = []
                    for word in query_words:
                        where_clauses_or.append("LOWER(raw_text) LIKE ?")
                        params_or.append(f"%{word}%")
                    query_or = f"SELECT name_kr FROM candidates WHERE {' OR '.join(where_clauses_or)} LIMIT {num_candidates}"
                    c.execute(query_or, params_or)
                    fallback_rows = c.fetchall()
                    
                seen = set([item['name'] for item in top_names])
                for cand in fallback_rows:
                    if cand[0] not in seen:
                        top_names.append({'name': cand[0], 'graph_score': 0.0, 'vector_score': 0.0})
                        seen.add(cand[0])
                        
            conn.close()
            logger.info(f"✅ SQLite Fallback으로 통과자 추가됨. 현재 top_names 길이: {len(top_names)}")
        except Exception as e:
            logger.error(f"⚠️ SQLite Fallback 실패: {e}")
        
        logger.info(f"✅ 최종 1차 퍼널 통과자: {len(top_names)}명")
                
    return top_names

import time
def api_search_v8(prompt: str, session_id: str = None, **kwargs) -> dict:
    import json
    import time
    import math
    from openai import OpenAI
    from neo4j import GraphDatabase
    
    st = time.time()
    logger.info(f"\n\n[V8 API Search] Payload: {prompt} / Session: {session_id}")
    
    # 1. Fetch Cache Map
    # Needs to be dynamically imported if inside
    from jd_compiler import get_candidates_from_cache
    cand_list = get_candidates_from_cache()
    # Map by id or name
    cache_map = {str(c.get('id', '')): c for c in cand_list}
    cache_map_name = {str(c.get('name_kr', '')).strip(): c for c in cand_list if c.get('name_kr')}

    extracted = parse_jd_to_json(prompt)
    conds = extracted.get("conditions", [])
    def map_abbreviations_to_conds(query_str, conditions_list):
        expansion_map = {
            "IPO": ["Investor_Relations", "IPO_Preparation"],
            "IR": ["Investor_Relations"],
            "DFT": ["Design_for_Testability"],
            "RTL": ["RTL_Design"],
            "SoC": ["System_on_Chip"],
            "SAP": ["SAP_ERP"],
            "BI": ["Business_Intelligence"],
            "Tableau": ["Tableau"],
            "DevOps": ["DevOps", "CI_CD"],
            "SaaS": ["SaaS"],
            "Kotlin": ["Kotlin", "Android_Development"],
            "ASRS": ["Warehouse_Automation"]
        }
        import re
        for abbr, expansions in expansion_map.items():
            # Use regex to match abbreviation strictly
            if re.search(r'\b' + re.escape(abbr) + r'\b', query_str, re.IGNORECASE):
                for exp in expansions:
                    # check if already exists
                    if not any(c.get('skill') == exp for c in conditions_list):
                        conditions_list.append({"action": "MANAGED", "skill": exp, "is_mandatory": False, "source": "abbreviation_map"})
        return conditions_list

    conds = map_abbreviations_to_conds(prompt, conds)
    is_category_search = extracted.get("is_category_search", False)
    conds = deduplicate_conditions(conds)
    conds = apply_downgrade_map(conds)
    conds = inject_node_affinity(conds)

    with open(SECRETS_PATH, "r", encoding="utf-8") as f:
        secrets = json.load(f)
    api_key = secrets.get("OPENAI_API_KEY") or secrets.get("openai_api_key")
    
    client = OpenAI(api_key=api_key)

    # Ontology Vector Index: LLM skills → 유사 온톨로지 노드 탐색
    _llm_skills_for_onto = _jd_llm.get('skills', []) if '_jd_llm' in dir() else []
    if _llm_skills_for_onto:
        existing_skill_names = {c.get('skill') for c in conds}
        _onto_added = []
        for _skill_txt in _llm_skills_for_onto[:6]:  # 최대 6개 skill만
            _matches = _ontology_index.search(_skill_txt, client,
                                              threshold=0.80, top_k=3)
            for _node, _sim in _matches:
                if _node not in existing_skill_names:
                    conds.append({"action": "MANAGED", "skill": _node,
                                  "is_mandatory": False, "source": "ontology_vector"})
                    existing_skill_names.add(_node)
                    _onto_added.append(f"{_node}({_sim:.2f})")
        if _onto_added:
            logger.info(f"[OntologyVector] Added {len(_onto_added)} nodes: {_onto_added}")
    
    # [Phase 1: Vector Search (Tower 1)]
    emb_res = client.embeddings.create(input=[prompt], model="text-embedding-3-small")
    query_vector = emb_res.data[0].embedding
    
    vector_results = []
    id_to_name = {}
    
    import os
    n_uri = _get_secret('NEO4J_URI')
    n_user = _get_secret('NEO4J_USERNAME')
    n_pw = _get_secret('NEO4J_PASSWORD')
    driver = GraphDatabase.driver(n_uri, auth=(n_user, n_pw))
    try:
        from pinecone import Pinecone as PineconeClient
        pc = PineconeClient(api_key=_get_secret('PINECONE_API_KEY'))
        pc_index = pc.Index(host=_get_secret('PINECONE_HOST'))
        res = pc_index.query(
            vector=query_vector,
            top_k=75,
            namespace='resume_vectors',
            include_metadata=True
        )
        seen_ids = set()
        for match in res.get('matches', []):
            meta = match.get('metadata', {})
            cid = meta.get('candidate_id') or match['id'].split('_chunk_')[0]
            if cid in seen_ids:
                continue
            seen_ids.add(cid)
            score = match['score']
            name = meta.get('name_kr', '')
            vector_results.append({'id': cid, 'name': name, 'score': score})
            id_to_name[cid] = name
    except Exception as e:
        logger.error(f"[Tower 1] Vector error: {e}")
    logger.info(f"[Tower 1] Extracted Top-75 via Pinecone.")

    # [Phase 2: Graph Score (Tower 2)]
    target_skills = list(set([c.get("skill") for c in conds if c.get("skill")]))
    graph_candidates = []
    
    if target_skills:
        try:
            with driver.session() as session:
                q = """
                MATCH (c:Candidate)-[r]->(s:Skill)
                WHERE s.name IN $target_skills AND type(r) <> 'USED_AS_TEMP' AND c.is_duplicate = 0
                WITH c, collect(DISTINCT {skill: s.name, action: type(r)}) AS skills
                RETURN coalesce(c.id, c.name_kr) AS id, coalesce(c.name_kr, c.name) AS name, skills
                """
                res = session.run(q, target_skills=target_skills)
                for r in res:
                    cid = str(r["id"]) if r["id"] else r["name"]
                    cand_edges = r["skills"]
                    id_to_name[cid] = r['name']
                    
                    raw_graph_score = calculate_gravity_fusion_score(cand_edges, conds, is_category_search)
                    candidate_nodes = [e['skill'] for e in cand_edges] if isinstance(cand_edges, list) else cand_edges
                    query_nodes = [c['skill'] for c in conds]
                    seniority = kwargs.get('seniority', 'All')
                    raw_graph_score += calc_gravity_score(candidate_nodes, query_nodes, seniority)
                    graph_score = math.log(max(raw_graph_score, 0) + 1)
                    
                    if graph_score > 0:
                        graph_candidates.append({
                            'id': cid,
                            'name': r['name'],
                            'graph_score': graph_score,
                            'cand_edges': cand_edges
                        })
                # Sort descending and take Top 30
                graph_candidates.sort(key=lambda x: x['graph_score'], reverse=True)
                graph_results = graph_candidates[:50]
                logger.info(f"[Tower 2] Graph Top-30 Evaluated.")
        except Exception as e:
            logger.error(f"[Tower 2] Graph error: {e}")
            graph_results = []
    else:
        graph_results = []
        logger.info(f"[Tower 2] No target skills to query graph.")

    # [Phase 3: Weighted Sum Fusion (Two-Tower)]
    combined_ids = list(set([c['id'] for c in vector_results] + [c['id'] for c in graph_results]))
    
    if not combined_ids:
        driver.close()
        return {'matched': [], 'total': 0, "is_category_search": is_category_search}
        
    edges_map = {}
    try:
        with driver.session() as session:
            q_edge = """
            MATCH (c:Candidate)-[r]->(s:Skill)
            WHERE (c.id IN $ids OR c.name_kr IN $ids) AND type(r) <> 'USED_AS_TEMP'
            RETURN coalesce(c.id, c.name_kr) AS id, collect(DISTINCT {skill: s.name, action: type(r)}) AS skills
            """
            res_e = session.run(q_edge, ids=combined_ids)
            def normalize_skill(skill_name: str) -> str:
                if skill_name in CANONICAL_MAP:
                    return CANONICAL_MAP[skill_name]
                lower = skill_name.lower()
                for key, val in CANONICAL_MAP.items():
                    if key.lower() == lower:
                        return val
                return skill_name

            edges_map = {}
            for r in res_e:
                normalized_skills = []
                for s in r["skills"]:
                    normalized_skills.append({
                        "skill": normalize_skill(s["skill"]),
                        "action": s["action"]
                    })
                edges_map[str(r["id"])] = normalized_skills
    except Exception as e:
        logger.error(f"Edges fetch error: {e}")
    finally:
        driver.close()

    vscore_map = {c['id']: c['score'] for c in vector_results}
    gscore_map = {c['id']: c['graph_score'] for c in graph_results}
    
    final_results = []
    from collections import Counter
    import math
    
    for cid in combined_ids:
        name = id_to_name.get(cid, cid)
        c_info = cache_map.get(cid) or cache_map.get(name) or {}
        sectors = c_info.get("main_sectors", [])
        
        cand_edges = edges_map.get(cid, [])
        matched_str_list = [f"{e['action']}:{e['skill']}" for e in cand_edges]
        
        v_score = vscore_map.get(cid, 0.0)
        
        raw_g = calculate_gravity_fusion_score(cand_edges, conds, is_category_search)
        candidate_nodes = [e['skill'] for e in cand_edges] if isinstance(cand_edges, list) else cand_edges
        query_nodes = [c['skill'] for c in conds]
        seniority = kwargs.get('seniority', 'All')
        raw_g += calc_gravity_score(candidate_nodes, query_nodes, seniority)
        g_score = math.log(max(raw_g, 0) + 1)
        
        final_score = (v_score * 0.6) + (g_score * 0.4)
            
        payload = {
            'id': cid,
            'candidate_id': cid,
            'name_kr': name,
            '이름': name,
            'current_company': c_info.get("current_company", "미상"),
            '연차등급': c_info.get("seniority", "확인 요망"),
            'sector': sectors[0] if sectors else "미분류",
            'Sub Sectors': sectors,
            'matched_edges': matched_str_list,
            'Experience Summary': c_info.get("summary", "정보 없음"),
            'profile_summary': c_info.get("profile_summary", ""),
            'phone': c_info.get("phone", "번호 없음"),
            'email': c_info.get("email", "이메일 없음"),
            'birth_year': c_info.get("birth_year", "생년 미상"),
            'notion_url': c_info.get("notion_url", "#"),
            'google_drive_url': c_info.get("google_drive_url", None),
            'careers': c_info.get("parsed_career_json") or c_info.get("careers", []),
            'education': c_info.get("education_json", []),
            'total_years': c_info.get("total_years", 0.0),
            'education_json': c_info.get("education_json", []),
            'ws_score': final_score,
            '_score': final_score,
            'graph_score': round(g_score, 4),
            'vector_score': round(v_score, 4),
            'total_edges': len(cand_edges)
        }
        
        a_cnt = Counter(e['action'] for e in cand_edges)
        s_cnt = Counter(e['skill'] for e in cand_edges)
        payload['top_actions'] = [f"{k}({v})" for k,v in a_cnt.most_common(3)]
        payload['top_skills'] = [f"{k}({v})" for k,v in s_cnt.most_common(3)]
        
        final_results.append(payload)

    if not final_results:
        return {'matched': [], 'total': 0, "is_category_search": is_category_search}

    max_final = max([r['ws_score'] for r in final_results] + [1.0])
    max_final = max_final if max_final > 0 else 1.0
    
    max_g = max([x['graph_score'] for x in final_results] + [1.0])
    max_v = max([x['vector_score'] for x in final_results] + [1.0])

    for r in final_results:
        norm_score = (r['ws_score'] / max_final) * 100
        r['score'] = round(norm_score, 4)
        r['_score'] = round(norm_score, 4)
        r['ws_score'] = round(r['ws_score'], 6)
        r['max_graph_score'] = round(max_g, 4)
        r['max_vector_score'] = round(max_v, 4)

    final_results.sort(key=lambda x: (-x['ws_score'], -x['total_edges']))
    
    grouped_by_name = {}
    import re as regex
    for r in final_results:
        if '무명' in r['name_kr']:
            grouped_by_name.setdefault(r['id'], []).append(r)
            continue
        pure_name = regex.sub(r'[^가-힣a-zA-Z]', '', r['name_kr'])
        grouped_by_name.setdefault(pure_name, []).append(r)
        
    dedup = []
    for name_key, candidates_group in grouped_by_name.items():
        if '무명' in candidates_group[0]['name_kr'] or len(candidates_group) == 1:
            dedup.append(candidates_group[0])
            continue
            
        person_clusters = []
        for c in candidates_group:
            phone = c.get('phone', '').strip().replace('-', '') if c.get('phone') else ''
            company = c.get('current_company', '').strip() if c.get('current_company') else ''
            
            matched_cluster = None
            for p in person_clusters:
                p_phone = p[0].get('phone', '').strip().replace('-', '') if p[0].get('phone') else ''
                p_company = p[0].get('current_company', '').strip() if p[0].get('current_company') else ''
                
                if (phone and p_phone and phone == p_phone) or (company and p_company and company == p_company):
                    matched_cluster = p
                    break
            if matched_cluster is not None:
                matched_cluster.append(c)
            else:
                person_clusters.append([c])
                
        for cluster in person_clusters:
            best = max(cluster, key=lambda x: x['ws_score'])
            dedup.append(best)
            
    dedup.sort(key=lambda x: (-x['ws_score'], -x['total_edges']))
    
    return {'matched': dedup[:100], 'total': len(dedup), "is_category_search": is_category_search}

def calculate_coverage_score(candidate_skills, target_skills):
    """
    [v10 Core] 후보자의 스킬과 타겟 스킬을 비교하여 정합성 점수(Coverage) 산출
    """
    if not target_skills:
        return 1.0, [], []
    
    cand_set = set(candidate_skills)
    target_set = set(target_skills)
    
    matched = cand_set.intersection(target_set)
    missing = target_set - cand_set
    
    score = len(matched) / len(target_set)
    return score, list(matched), list(missing)


def normalize_query_with_map(raw_keywords):
    """
    [어휘 불일치 해결 1단계] 사용자 입력(A)을 시스템 표준 노드(A')로 강제 변환
    """
    from ontology_graph import CANONICAL_MAP
    canonical_targets = set()
    for word in raw_keywords:
        canonical_word = CANONICAL_MAP.get(word, CANONICAL_MAP.get(word.upper(), word))
        canonical_targets.add(canonical_word)
    return list(canonical_targets)




def calculate_recency_multiplier(end_date_str):
    from datetime import datetime
    if not end_date_str or '현재' in end_date_str or '재직' in end_date_str or 'present' in end_date_str.lower():
        return 1.2
        
    # Attempt to parse date
    import re
    match = re.search(r'20\d{2}', end_date_str)
    if not match: return 1.0
    
    try:
        year = int(match.group(0))
        current_year = datetime.now().year
        diff = current_year - year
        if diff <= 3: return 1.2
        if diff >= 5: return 0.8
    except:
        pass
    return 1.0



def expand_query_for_embedding(query: str, openai_client) -> str:
    """쿼리를 이력서 스타일 텍스트로 확장해서 벡터 매칭 품질 향상"""
    try:
        resp = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{
                "role": "system",
                "content": (
                    "You are a Korean talent search expert. "
                    "Convert a job search query into a resume-style description "
                    "that would match ideal candidates. "
                    "Write in Korean, 150-200 characters, "
                    "focusing on: current role, key skills, "
                    "major achievements, and experience level. "
                    "Do NOT use bullet points. Write as continuous text."
                )
            }, {
                "role": "user",
                "content": f"검색 쿼리: {query}"
            }],
            max_tokens=300,
            temperature=0.3
        )
        return resp.choices[0].message.content.strip()
    except Exception as e:
        logger.error(f"Query expansion failed: {e}")
        return query

def should_expand_query(query: str) -> bool:
    specific_keywords = [
        'npu', 'soc', 'pcie', 'kafka', 'kubernetes', 'cfo', 'cto', 
        'llm', 'mlops', 'devops', 'rtl', 'fpga', 'nvme', 'cuda',
        'kafka', 'elasticsearch', 'fpa', 'fp&a', 'm&a', 'ipo'
    ]
    query_lower = query.lower()
    if any(k in query_lower for k in specific_keywords):
        return False
    if len(query) >= 30:
        return False
    return True

def cosine_similarity(v1, v2):
    if not v1 or not v2: return 0.0
    import math
    dot = sum(a*b for a, b in zip(v1, v2))
    norm1 = math.sqrt(sum(a*a for a in v1))
    norm2 = math.sqrt(sum(b*b for b in v2))
    if norm1 == 0 or norm2 == 0: return 0.0
    return dot / (norm1 * norm2)

def get_best_similarity(query_vec, main_sim, career_embs_json):
    return main_sim  # 멀티 벡터 비활성화

def get_cei_boost(candidate_id: str, conn, query_domain: str) -> float:
    cur = conn.cursor()
    cur.execute(
        "SELECT cei_json, cei_confidence FROM candidates WHERE id=?",
        (candidate_id,))
    row = cur.fetchone()
    if not row or not row[0]:
        return 0.0

    try:
        cei = json.loads(row[0])
        confidence = row[1] or 0.0
        scores = cei.get('scores', {})

        # 도메인별 CEI 가중치
        DOMAIN_CEI_WEIGHTS = {
            'semiconductor': {
                'tech': 0.50, 'company': 0.25,
                'tenure': 0.15, 'evidence': 0.10},
            'ai': {
                'tech': 0.45, 'company': 0.25,
                'tenure': 0.15, 'evidence': 0.15},
            'finance': {
                'company': 0.40, 'tenure': 0.25,
                'tech': 0.20, 'evidence': 0.15},
            'executive': {
                'company': 0.45, 'tenure': 0.30,
                'evidence': 0.15, 'tech': 0.10},
            'default': {
                'company': 0.30, 'tech': 0.30,
                'tenure': 0.25, 'evidence': 0.15},
        }

        weights = DOMAIN_CEI_WEIGHTS.get(
            query_domain,
            DOMAIN_CEI_WEIGHTS['default'])

        weighted_score = sum(
            scores.get(k, 0.0) * w
            for k, w in weights.items()
        )

        # 신뢰도 반영
        # 신뢰도 낮으면 부스트도 낮게
        boost = weighted_score * confidence * 0.005
        return round(boost, 4)

    except:
        return 0.0

def api_search_v9(prompt: str, session_id: str = None, seniority: str = 'All', weights: dict = None) -> dict:
    """
    [Hybrid Search v9]
    Tower 1: Vector (Neo4j)
    Tower 2: Graph (Neo4j)
    Tower 3: BM25 (Local)
    Tower 4: Depth (Action + Achievement)
    """
    import json, time, math
    
    # 0. Set Weights (Dynamic)
    SEMI_KEYWORDS = ['npu', 'soc', '반도체', 'rtl', 'fpga',
                     'asic', '팹리스', 'chip', '칩', 'verilog',
                     'tape-out', 'tape out', 'ppa']
    AI_KEYWORDS   = ['llm', 'ai ', '인공지능', 'ml ', '머신러닝',
                     '딥러닝', 'deep learning', 'gpu', 'inference',
                     '추론', '서빙', 'transformer', 'pytorch', 'mlops']
    SW_KEYWORDS   = ['백엔드', 'backend', '프론트', 'frontend',
                     'devops', '인프라', 'infra', 'kubernetes',
                     'docker', 'msa', '마이크로서비스']
    EMBEDDED_KEYWORDS = ['드라이버', '커널', 'kernel', 'firmware',
                         '펌웨어', 'bsp', 'rtos', 'embedded',
                         '임베디드']
    MARKETING_KEYWORDS = ['마케팅', 'marketing', '광고', '브랜드', 
                          '퍼포먼스', 'CRM', '그로스', 'growth']
    PO_KEYWORDS = ['product owner', 'po ', 'p.o.', 
                   '프로덕트 오너', '프로덕트 매니저', 'pm ',
                   'product manager']
    HR_KEYWORDS  = ['채용', '인사', '총무', 'general affairs', '시설관리', '구매관리', '복리후생', '노무']
    DESIGN_KEYWORDS = ['uiux', 'ui/ux', 'ux 디자이너', 'ui 디자이너', 
                       '디자이너', 'product design', 'figma']
    CTO_KEYWORDS = ['cto', 'chief technology', '기술 임원', '기술총괄']
    CFO_KEYWORDS = ['cfo', 'chief financial', '재무총괄', '최고재무']
    KAFKA_KEYWORDS = ['kafka', '카프카', 'message queue', '메시지큐', 'event streaming']

    query_lower = prompt.lower()

    if any(k in query_lower for k in SEMI_KEYWORDS):
        query_domain = 'semiconductor'
    elif any(k in query_lower for k in EMBEDDED_KEYWORDS):
        query_domain = 'embedded'
    elif any(k in query_lower for k in AI_KEYWORDS):
        query_domain = 'ai'
    elif any(k in query_lower for k in CFO_KEYWORDS) or any(k in query_lower for k in ['finance', '재무', 'fp&a', 'treasury', '회계', 'accounting', 'ipo', 'fundraising', 'investor relations']) or (' ir ' in ' ' + query_lower + ' '):
        query_domain = 'finance'
    elif any(k in query_lower for k in MARKETING_KEYWORDS):
        query_domain = 'marketing'
    elif any(k in query_lower for k in PO_KEYWORDS):
        query_domain = 'product'
    elif any(k in query_lower for k in SW_KEYWORDS):
        query_domain = 'sw'
    elif any(k in query_lower for k in HR_KEYWORDS) or (' hr ' in ' ' + query_lower + ' '):
        query_domain = 'hr'
    elif any(k in query_lower for k in DESIGN_KEYWORDS):
        query_domain = 'design'
    elif any(k in query_lower for k in CTO_KEYWORDS):
        query_domain = 'cto'
    elif any(k in query_lower for k in KAFKA_KEYWORDS):
        query_domain = 'data_infra'
    else:
        query_domain = 'general'

    DOMAIN_WEIGHTS = {
        'semiconductor': {'v': 0.50, 'g': 0.38, 'b': 0.05, 'd': 0.07},
        'ai':            {'v': 0.52, 'g': 0.35, 'b': 0.05, 'd': 0.08},
        'general':       {'v': 0.65, 'g': 0.20, 'b': 0.08, 'd': 0.07},
        'finance':       {'v': 0.62, 'g': 0.22, 'b': 0.08, 'd': 0.08},
        'hr':            {'v': 0.65, 'g': 0.18, 'b': 0.10, 'd': 0.07},
        'default':       {'v': 0.60, 'g': 0.28, 'b': 0.05, 'd': 0.07},
    }

    weight_domain = query_domain
    if query_domain == 'cfo':
        weight_domain = 'finance'

    selected_weights = DOMAIN_WEIGHTS.get(weight_domain, DOMAIN_WEIGHTS['default'])
    w_v_dynamic = selected_weights['v']
    w_g_dynamic = selected_weights['g']
    w_b_dynamic = selected_weights['b']
    w_d_dynamic = selected_weights['d']

    # weights 파라미터로 외부 주입 시 우선 적용
    w_v = weights.get('vector', w_v_dynamic) if weights else w_v_dynamic
    w_g = weights.get('graph', w_g_dynamic) if weights else w_g_dynamic
    w_b = weights.get('bm25', w_b_dynamic) if weights else w_b_dynamic
    w_d = weights.get('depth', w_d_dynamic) if weights else w_d_dynamic

    logger.info(f'[Dynamic Weights] domain={query_domain} | V={w_v} G={w_g} B={w_b} D={w_d}')

    from openai import OpenAI
    from neo4j import GraphDatabase
    
    st = time.time()
    logger.critical(f"\n\nDEBUG [V9-PROMPT-CHECK] Payload: {prompt} / Session: {session_id}")
    
    # [Robustness] Ensure seniority is a string for gravity score dict lookups
    if not seniority or seniority == '무관' or seniority == 'All':
        seniority = "All"
    elif isinstance(seniority, list):
        if not seniority or "무관" in seniority or "All" in seniority or "ALL" in seniority:
            seniority = "All"
        else:
            seniority = str(seniority[0]).upper()
    else:
        seniority = str(seniority).upper()

    # 0. Load Cache Maps
    from jd_compiler import get_candidates_from_cache
    cand_list = get_candidates_from_cache()
    cache_map = {str(c.get('id', '')): c for c in cand_list}
    logger.info(f"DEBUG [V9] Step 0: Cache Loaded ({len(cand_list)} candidates)")
    
    # candidate_sector_map은 검색 시작 시 SQLite에서 {candidate_id: sector} 딕셔너리로 미리 로드해줘.
    db_path = os.environ.get('DB_PATH', 'candidates.db')
    conn_sec = sqlite3.connect(db_path)
    try:
        cur_sec = conn_sec.cursor()
        cur_sec.execute("SELECT id, sector FROM candidates")
        candidate_sector_map = {str(r[0]): r[1] for r in cur_sec.fetchall()}
    finally:
        conn_sec.close()
    
    # 1. Parse & Expand Query
    logger.info(f"DEBUG [V9] Step 1: Parsing query...")
    with open(SECRETS_PATH, "r", encoding="utf-8") as f:
        secrets = json.load(f)
    client = OpenAI(api_key=secrets.get("OPENAI_API_KEY"))
    # 규칙 기반 파서 (스킬 매핑 주담당)
    extracted = parse_jd_to_json(prompt)
    conds = extracted.get("conditions", [])
    min_years_rule = extracted.get("min_years", 0)
    # LLM 파서: preferred_companies + 명시적 min_years 보강
    _jd_llm = parse_jd_with_llm(prompt, client)
    preferred_companies = _jd_llm.get("preferred_companies", [])
    _min_years_llm = _jd_llm.get("min_years", 0)
    min_years = _min_years_llm if _min_years_llm > 0 else min_years_rule
    logger.info(f"[V9-LLM] preferred_companies={preferred_companies}, min_years={min_years}")
    
    # Map abbreviations
    def map_abbreviations_to_conds(query_str, conditions_list):
        expansion_map = {
            "IPO": ["Investor_Relations", "IPO_Preparation"],
            "IR": ["Investor_Relations"],
            "DFT": ["Design_for_Testability"],
            "RTL": ["RTL_Design"],
            "SoC": ["System_on_Chip"],
            "SAP": ["SAP_ERP"],
            "BI": ["Business_Intelligence"],
            "Tableau": ["Tableau"],
            "DevOps": ["DevOps", "CI_CD"],
            "SaaS": ["SaaS"],
            "Kotlin": ["Kotlin", "Android_Development"],
            "ASRS": ["Warehouse_Automation"]
        }
        import re
        for abbr, expansions in expansion_map.items():
            if re.search(r'\b' + re.escape(abbr) + r'\b', query_str, re.IGNORECASE):
                for exp in expansions:
                    if not any(c.get('skill') == exp for c in conditions_list):
                        conditions_list.append({"action": "MANAGED", "skill": exp, "is_mandatory": False, "source": "abbreviation_map"})
        return conditions_list

    conds = map_abbreviations_to_conds(prompt, conds)
    is_category_search = extracted.get("is_category_search", False)
    conds = deduplicate_conditions(conds)
    conds = apply_downgrade_map(conds)
    conds = inject_node_affinity(conds)
    
    # 2. Tower 1: Vector Search (Pinecone - replacing Neo4j queryNodes)
    n_uri = _get_secret('NEO4J_URI')
    n_user = _get_secret('NEO4J_USERNAME')
    n_pw = _get_secret('NEO4J_PASSWORD')
    driver = GraphDatabase.driver(n_uri, auth=(n_user, n_pw))
    
    with open(SECRETS_PATH, "r", encoding="utf-8") as f:
        secrets = json.load(f)
    client = OpenAI(api_key=secrets.get("OPENAI_API_KEY"))
    search_text = prompt
    logger.info(f"[Vector Search] Kept Raw Query (Query Expansion Disabled): {search_text}")
    emb_res = client.embeddings.create(input=[search_text], model="text-embedding-3-small")
    query_vector = emb_res.data[0].embedding

    v_scores = {}
    id_to_name = {}
    try:
        from pinecone import Pinecone as PineconeClient
        pc = PineconeClient(api_key=_get_secret('PINECONE_API_KEY'))
        pc_index = pc.Index(host=_get_secret('PINECONE_HOST'))
        res = pc_index.query(
            vector=query_vector,
            top_k=75,
            namespace='resume_vectors',
            include_metadata=True
        )
        seen_ids = set()
        for match in res.get('matches', []):
            meta = match.get('metadata', {})
            cid = meta.get('candidate_id') or match['id'].split('_chunk_')[0]
            if cid in seen_ids:
                continue
            seen_ids.add(cid)
            score = match['score']
            name = meta.get('name_kr', '')
            v_scores[cid] = score
            id_to_name[cid] = name
    except Exception as e:
        logger.error(f"[V9] Pinecone Vector Error: {e}")

    # 3. Tower 2: Graph Candidates (Skill Match)
    g_matched_ids = []
    target_skills = list(set([c.get("skill") for c in conds if c.get("skill")]))
    logger.critical(f"DEBUG [V9] --- START GRAPH TOWER ---")
    logger.critical(f"DEBUG [V9] Extracted Target Skills: {target_skills}")
    if target_skills:
        try:
            logger.critical(f"DEBUG [V9] Entering Neo4j Session for Graph Match...")
            with driver.session() as session:
                res_g = session.run("""
                    MATCH (c:Candidate)-[r]->(s:Skill)
                    WHERE s.name IN $target_skills AND type(r) <> 'USED_AS_TEMP' 
                    RETURN DISTINCT coalesce(c.id, c.name_kr) AS id, coalesce(c.name_kr, c.name) AS name
                """, target_skills=target_skills)
                for r in res_g:
                    cid = str(r["id"])
                    if cid == 'c3d4ee55-266a-44f6-8e66-fb7486be38a8':
                        logger.critical(f"DEBUG [V9] FOUND CHOI IN GRAPH MATCH! Name: {r['name']}")
                    g_matched_ids.append(cid)
                    id_to_name[cid] = r["name"]
                logger.critical(f"DEBUG [V9] Graph Tower Matched {len(g_matched_ids)} IDs. Sample: {g_matched_ids[:5]}")
        except Exception as e:
            logger.error(f"[V9] Graph Match Error: {e}")

    # 4. Tower 3: BM25 Candidates
    bm_scores = get_bm25_top(prompt, top_k=200)

    # 5. Combined Pool Selection
    # V8 used Top 75/50, V9 uses Top 100/100/50 for broader hybrid coverage
    vector_ids = list(v_scores.keys())
    # Note: we don't have scores for g_matched_ids yet, so we just take all for now 
    # but in V8 it was limited to 50. Let's take all if they are within a reasonable count.
    graph_ids = g_matched_ids[:300] 
    bm25_ids = sorted(bm_scores.keys(), key=lambda k: bm_scores[k], reverse=True)[:100]
    
    # ── Sector pre-filter (풀 진입 단계) ──────────────
    SEMI_KEYWORDS = ['npu', 'soc', '반도체', 'rtl', 'fpga',
                     'asic', '팹리스', 'chip', '칩', 'verilog',
                     'tape-out', 'tape out', 'ppa']
    AI_KEYWORDS   = ['llm', 'ai ', '인공지능', 'ml ', '머신러닝',
                     '딥러닝', 'deep learning', 'gpu', 'inference',
                     '추론', '서빙', 'transformer', 'pytorch', 'mlops']
    SW_KEYWORDS   = ['백엔드', 'backend', '프론트', 'frontend',
                     'devops', '인프라', 'infra', 'kubernetes',
                     'docker', 'msa', '마이크로서비스']
    EMBEDDED_KEYWORDS = ['드라이버', '커널', 'kernel', 'firmware',
                         '펌웨어', 'bsp', 'rtos', 'embedded',
                         '임베디드']
    MARKETING_KEYWORDS = ['마케팅', 'marketing', '광고', '브랜드', 
                          '퍼포먼스', 'CRM', '그로스', 'growth']
    PO_KEYWORDS = ['product owner', 'po ', 'p.o.', 
                   '프로덕트 오너', '프로덕트 매니저', 'pm ',
                   'product manager']
    HR_KEYWORDS  = ['채용', '인사', '총무', 'general affairs', '시설관리', '구매관리', '복리후생', '노무']
    DESIGN_KEYWORDS = ['uiux', 'ui/ux', 'ux 디자이너', 'ui 디자이너', 
                       '디자이너', 'product design', 'figma']
    CTO_KEYWORDS = ['cto', 'chief technology', '기술 임원', '기술총괄']
    CFO_KEYWORDS = ['cfo', 'chief financial', '재무총괄', '최고재무']
    KAFKA_KEYWORDS = ['kafka', '카프카', 'message queue', '메시지큐', 'event streaming']

    query_lower = prompt.lower()

    if any(k in query_lower for k in SEMI_KEYWORDS):
        query_domain = 'semiconductor'
    elif any(k in query_lower for k in EMBEDDED_KEYWORDS):
        query_domain = 'embedded'
    elif any(k in query_lower for k in AI_KEYWORDS):
        query_domain = 'ai'
    elif any(k in query_lower for k in CFO_KEYWORDS) or any(k in query_lower for k in ['finance', '재무', 'fp&a', 'treasury', '회계', 'accounting', 'ipo', 'fundraising', 'investor relations']) or (' ir ' in ' ' + query_lower + ' '):
        query_domain = 'cfo'
    elif any(k in query_lower for k in MARKETING_KEYWORDS):
        query_domain = 'marketing'
    elif any(k in query_lower for k in PO_KEYWORDS):
        query_domain = 'product'
    elif any(k in query_lower for k in SW_KEYWORDS):
        query_domain = 'sw'
    elif any(k in query_lower for k in HR_KEYWORDS) or (' hr ' in ' ' + query_lower + ' '):
        query_domain = 'hr'
    elif any(k in query_lower for k in DESIGN_KEYWORDS):
        query_domain = 'design'
    elif any(k in query_lower for k in CTO_KEYWORDS):
        query_domain = 'cto'
    elif any(k in query_lower for k in KAFKA_KEYWORDS):
        query_domain = 'data_infra'
    else:
        query_domain = 'general'

    ALLOWED_SECTORS = {
        'semiconductor': {'Eng_Semi', 'Eng_Embedded', 'Eng_AI'},
        'embedded':      {'Eng_Embedded', 'Eng_Semi', 'Eng_HW', 'Eng_SW'},
        'ai':            {'Eng_AI', 'Eng_SW', 'Eng_Data', 'Eng_Semi', 'Eng_Embedded'},
        'marketing':     {'Marketing', 'Strategy', 'Product'},
        'product':       {'Product', 'Strategy', 'Eng_SW', 'Eng_AI'},
        'sw':            {'Eng_SW', 'Eng_AI', 'Eng_Data', 'Eng_Embedded'},
        'hr':            {'HR'},
        'design':        {'Product', 'Marketing'},
        'cto':           {'Eng_SW', 'Eng_AI', 'Product', 'Strategy'},
        'cfo':           {'Finance', 'Strategy'},
        'finance':       {'Finance', 'Strategy'},
        'data_infra':    {'Eng_Data', 'Eng_SW', 'Eng_AI'},
        'general':       None  # 필터 없음
    }

    # 복수 도메인 감지
    detected_domains = []
    if any(k in query_lower for k in SEMI_KEYWORDS):
        detected_domains.append('semiconductor')
    if any(k in query_lower for k in AI_KEYWORDS):
        detected_domains.append('ai')
    if any(k in query_lower for k in SW_KEYWORDS):
        detected_domains.append('sw')

    # 복합 도메인이면 allowed_sectors 합집합
    if len(detected_domains) > 1:
        allowed = set()
        for d in detected_domains:
            allowed |= ALLOWED_SECTORS.get(d, set())
    else:
        allowed = ALLOWED_SECTORS.get(query_domain)

    # Vector/BM25 풀에서 allowed sector 아닌 후보 제거
    if allowed:
        def get_primary_sector(cid):
            sector_str = candidate_sector_map.get(cid, '')
            return sector_str.split(',')[0].strip() if sector_str else ''
        
        vector_ids = [cid for cid in vector_ids 
                      if get_primary_sector(cid) in allowed]
        bm25_ids   = [cid for cid in bm25_ids 
                      if get_primary_sector(cid) in allowed]
        graph_ids  = [cid for cid in graph_ids 
                      if get_primary_sector(cid) in allowed]
    
    combined_ids = list(set(vector_ids) | set(graph_ids) | set(bm25_ids))
    if combined_ids:
        conn_dup = sqlite3.connect(os.environ.get('DB_PATH', 'candidates.db'))
        try:
            placeholders_dup = ','.join(['?'] * len(combined_ids))
            cur_dup = conn_dup.cursor()
            cur_dup.execute(f"SELECT id FROM candidates WHERE id IN ({placeholders_dup}) AND is_duplicate = 0", combined_ids)
            active_ids = {str(r[0]) for r in cur_dup.fetchall()}
            combined_ids = [cid for cid in combined_ids if cid in active_ids]
        except Exception as dup_ex:
            logger.warning(f"Error filtering duplicates: {dup_ex}")
        finally:
            conn_dup.close()
    if not combined_ids:
        if 'driver' in locals(): driver.close()
        return {'matched': [], 'total': 0, "is_category_search": is_category_search}

    # 6. Hydrate Edges and Metadata (Crucial for V8/V9 precision)
    edges_map = {}
    raw_text_map = {}
    try:
        with driver.session() as session:
            res_e = session.run("""
                MATCH (c:Candidate)-[r]->(s:Skill)
                WHERE (c.id IN $ids OR c.name_kr IN $ids) AND type(r) <> 'USED_AS_TEMP'
                RETURN coalesce(c.id, c.name_kr) AS id, collect(DISTINCT {skill: s.name, action: type(r), last_used_year: r.last_used_year}) AS skills
            """, ids=combined_ids)

            def normalize_skill(skill_name: str) -> str:
                if skill_name in CANONICAL_MAP:
                    return CANONICAL_MAP[skill_name]
                lower = skill_name.lower()
                for key, val in CANONICAL_MAP.items():
                    if key.lower() == lower:
                        return val
                return skill_name

            edges_map = {}
            for r in res_e:
                normalized_skills = []
                for s in r["skills"]:
                    normalized_skills.append({
                        "skill": normalize_skill(s["skill"]),
                        "action": s["action"],
                        "last_used_year": s.get("last_used_year")
                    })
                edges_map[str(r["id"])] = normalized_skills
    except Exception as e:
        logger.error(f"[V9] Edge hydration error: {e}")
    finally:
        if 'driver' in locals(): driver.close()

    # Fetch full metadata from SQLite (Crucial because cache JSON might be missing on Railway)
    db_metadata_map = {}
    conn = sqlite3.connect(os.environ.get('DB_PATH', 'candidates.db'))
    placeholders = ','.join(['?'] * len(combined_ids))
    try:
        query = f"""
            SELECT id, name_kr, raw_text, sector, current_company, total_years, 
                   profile_summary, careers_json, education_json, email, phone, birth_year, google_drive_url,
                   program_signal, program_stage, has_startup, has_big_company
            FROM candidates 
            WHERE id IN ({placeholders})
        """
        try:
            rows_t = conn.execute(query, combined_ids).fetchall()
        except sqlite3.OperationalError as e:
            if "no such column" in str(e).lower():
                logger.warning("[V9] program_signal/stage column missing in SQLite. Using fallback 0.0.")
                query = f"""
                    SELECT id, name_kr, raw_text, sector, current_company, total_years, 
                           profile_summary, careers_json, education_json, email, phone, birth_year, google_drive_url,
                           0.0 as program_signal, NULL as program_stage, has_startup, has_big_company
                    FROM candidates 
                    WHERE id IN ({placeholders})
                """
                rows_t = conn.execute(query, combined_ids).fetchall()
            else:
                raise e

        for r in rows_t:
            cid = str(r[0])
            name_val = r[1]
            raw_text_val = r[2]
            
            raw_text_map[cid] = raw_text_val
            if (cid not in id_to_name or not id_to_name.get(cid)) and name_val:
                id_to_name[cid] = name_val
            
            # Map SQLite fields to the format expected by the frontend
            import json
            try:
                careers = json.loads(r[7]) if r[7] else []
            except:
                careers = []
            try:
                education = json.loads(r[8]) if r[8] else []
            except:
                education = []

            db_metadata_map[cid] = {
                'id': cid,
                'name_kr': name_val,
                'sector': r[3] or '미분류',
                'current_company': r[4] or '미상',
                'total_years': r[5] or 0,
                'profile_summary': r[6] or '',
                'careers': careers,
                'education': education,
                'email': r[9] or '',
                'phone': r[10] or '',
                'birth_year': r[11] or '',
                'google_drive_url': r[12] or '',
                'program_signal': r[13] or 0.0,
                'program_stage': r[14] or None,
                'has_startup': r[15] or 0,
                'has_big_company': r[16] or 0
            }
    finally:
        pass

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

    # Calculate accurate Graph (G) and Depth (D) score for every candidate in the pool
    final_g_scores = {}
    final_d_scores = {}
    
    ACTION_WEIGHT_MAP = {
        'MANAGED': 1.0, 'BUILT': 0.9, 'DESIGNED': 0.8, 'LAUNCHED': 0.7,
        'GREW': 0.7, 'ANALYZED': 0.5, 'NEGOTIATED': 0.5, 'SUPPORTED': 0.2
    }
    
    for cid in combined_ids:
        cand_edges = edges_map.get(cid, [])
        # Tower 2: Graph (Existing V8 logic)
        raw_g = calculate_gravity_fusion_score(cand_edges, conds, is_category_search)
        candidate_nodes = [e['skill'] for e in cand_edges]
        query_nodes = [c['skill'] for c in conds]
        raw_g += calc_gravity_score(candidate_nodes, query_nodes, seniority)
        # ── Primary sector 기반 G score 패널티 ──────────────
        def get_primary_sector(cid):
            sector_str = candidate_sector_map.get(cid, '')
            return sector_str.split(',')[0].strip() if sector_str else ''

        primary = get_primary_sector(cid)
        g_score = math.log(max(raw_g, 0) + 1)

        if query_domain == 'semiconductor':
            if primary == 'Eng_Semi':
                pass  # 패널티 없음
            elif primary == 'Eng_Embedded':
                g_score *= 0.85  # 경미한 감쇠
            elif primary in ('Eng_AI', 'Eng_SW'):
                g_score *= 0.65  # 중간 감쇠
            else:
                g_score *= 0.4   # 강한 감쇠

        elif query_domain == 'ai':
            if primary == 'Eng_AI':
                pass
            elif primary in ('Eng_SW', 'Eng_Data'):
                g_score *= 0.9
            elif primary == 'Eng_Semi':
                g_score *= 0.8   # 반도체 출신 AI는 경미한 감쇠만
            else:
                g_score *= 0.5

        final_g_scores[cid] = g_score
        
        # Tower 4: Depth Score
        # [Signal 1] Action intensity on matched skills
        matched_action_score = sum(
            ACTION_WEIGHT_MAP.get(edge['action'], 0.3)
            for edge in cand_edges
            if edge['skill'] in target_skills
        ) / max(len(target_skills), 1)
        depth_action = min(matched_action_score, 1.0)
        
        # [Signal 2] Achievement Density (raw_text numbers)
        achievement_density = calc_achievement_density(raw_text_map.get(cid, ""))
        
        final_d_scores[cid] = (depth_action * 0.6) + (achievement_density * 0.4)

    # 7. Hybrid Fusion
    max_v = max(list(v_scores.values()) + [1.0])
    max_g = max(list(final_g_scores.values()) + [1.0])
    max_b = max(list(bm_scores.values()) + [1.0])
    
    final_candidates = []
    for cid in combined_ids:
        # min_years 경험 필터 (명시적 연차 요건이 있는 경우)
        if min_years > 0:
            _total_yrs = db_metadata_map.get(cid, {}).get("total_years", 0) or 0
            if _total_yrs < min_years:
                continue

        norm_v = (v_scores.get(cid, 0.0) / max_v) if max_v > 0 else 0.0
        norm_g = (final_g_scores.get(cid, 0.0) / max_g) if max_g > 0 else 0.0
        norm_b = (bm_scores.get(cid, 0.0) / max_b) if max_b > 0 else 0.0
        depth_score = final_d_scores.get(cid, 0.0)
        
        # Dynamic Fusion v9 (4-Tower + PROGRAM Boost)
        prog_signal = float(db_metadata_map.get(cid, {}).get('program_signal', 0.0))
        program_boost = prog_signal * 0.05  # Max +0.05 for '최종합격'
        
        final_score = (norm_v * w_v) + (norm_g * w_g) + (norm_b * w_b) + (depth_score * w_d) + program_boost
        # Preferred companies boost (from LLM extraction)
        final_score += company_boost_map.get(cid, 0.0)
        
        # [Signal 4] Company Intelligence Boost
        row_dict = db_metadata_map.get(cid, {})
        c_boost = get_company_boost(
            row_dict.get('current_company', ''),
            conds,
            conn
        )
        final_score += c_boost

        # CEI 부스트 추가
        cei_boost = get_cei_boost(cid, conn, query_domain)
        final_score += cei_boost
        
        if cid == 'f5875fc2-99aa-4605-9742-5ec93f4cd51a':
            logger.info(f"DEBUG [김은형] v_norm:{norm_v:.4f} g_norm:{norm_g:.4f} b_norm:{norm_b:.4f} depth:{depth_score:.4f} boost:{c_boost:.4f} final:{final_score:.4f}")
        
        if cid == 'c3d4ee55-266a-44f6-8e66-fb7486be38a8':
            logger.critical(f"DEBUG [CHOI-SCORE] v_norm:{norm_v:.4f} g_norm:{norm_g:.4f} b_norm:{norm_b:.4f} depth:{depth_score:.4f} boost:{c_boost:.4f} final:{final_score:.4f}")
            logger.critical(f"DEBUG [CHOI-SCORE] Raw V: {v_scores.get(cid, 0):.4f} | Raw G: {final_g_scores.get(cid, 0):.4f}")
        
        # Debug for Rank 1 (based on previous run it was 김종민, but let's just find the max score)
        if final_score > 0.75:
            logger.info(f"DEBUG [POTENTIAL RANK 1] {cid} v_norm:{norm_v:.4f} g_norm:{norm_g:.4f} b_norm:{norm_b:.4f} depth:{depth_score:.4f} boost:{c_boost:.4f} final:{final_score:.4f}")

        name = id_to_name.get(cid, cache_map.get(cid, {}).get('name_kr', cid))
        final_candidates.append({
            'id': cid,
            'candidate_id': cid,
            'name_kr': name,
            'score': final_score,
            'v_score': v_scores.get(cid, 0.0),
            'g_score': final_g_scores.get(cid, 0.0),
            'bm_score': bm_scores.get(cid, 0.0),
            'depth_score': depth_score
        })

    
    final_candidates.sort(key=lambda x: x['score'], reverse=True)
    top_matched = final_candidates[:50]

    matched_candidates = []
    for c in top_matched:
        cid = c['id']
        name = c['name_kr']
        
        # Use DB metadata first, fallback to cache_map
        c_info = db_metadata_map.get(cid) or cache_map.get(cid) or cache_map.get(name) or {}
        
        cand_edges = edges_map.get(cid, [])
        # V9: Map edges/skills to format UI expects (MATCHEDGE)
        matched_edges = [e['skill'] for e in cand_edges]
        matched_actions = list(set([e['action'] for e in cand_edges]))
        
        candidate_obj = {
            'id': cid,
            'name': name,
            'name_kr': name,
            'final_score': round(c['score'], 4),
            'v_score': round(c['v_score'], 4),
            'g_score': round(c['g_score'], 4),
            'bm_score': round(c['bm_score'], 4),
            'depth_score': round(c['depth_score'], 4),
            'matched_edges': matched_edges,
            'matched_actions': matched_actions,
            'sector': c_info.get('sector', '미분류'),
            'current_company': c_info.get('current_company', '미상'),
            'total_years': c_info.get('total_years', 0),
            'profile_summary': c_info.get('profile_summary', ''),
            'careers': c_info.get('careers', []),
            'education': c_info.get('education', []),
            'email': c_info.get('email', ''),
            'phone': c_info.get('phone', ''),
            'birth_year': c_info.get('birth_year', ''),
            'google_drive_url': c_info.get('google_drive_url', ''),
            'program_stage': c_info.get('program_stage', None),
            'seniority': get_seniority_label(c_info.get('total_years', 0)),
            '연차등급': get_seniority_label(c_info.get('total_years', 0)),
            'has_startup': c_info.get('has_startup', 0),
            'has_big_company': c_info.get('has_big_company', 0)
        }
        matched_candidates.append(candidate_obj)

    logger.info(f"[V9 Hybrid Search] Completed. Top result: {matched_candidates[0]['name_kr'] if matched_candidates else 'None'}")
    
    if 'conn' in locals():
        try:
            conn.close()
        except:
            pass

    return {
        "matched": matched_candidates[:50],
        "total": len(final_candidates),
        "is_category_search": is_category_search
    }

# =================================================================
# 🧬 [v10.4 Bayesian Expert Edition] Domain-Specific Adaptive Engine
# =================================================================

class DomainSubsetExtractor:
    def __init__(self, anchors_path='domain_anchors.json'):
        self.anchors = []
        if os.path.exists(anchors_path):
            with open(anchors_path, 'r', encoding='utf-8') as f:
                self.anchors = json.load(f)
        logging.info(f"[DomainSubset] Loaded {len(self.anchors)} anchors.")

    def get_local_likelihood(self, query_embedding, top_n=5):
        """
        Finds the most similar golden samples and extracts domain-specific skill importance.
        """
        if not self.anchors: return {}
        
        # Calculate cosine similarity
        similarities = []
        q_vec = np.array(query_embedding)
        for anchor in self.anchors:
            a_vec = np.array(anchor["embedding"])
            sim = np.dot(q_vec, a_vec) / (np.linalg.norm(q_vec) * np.linalg.norm(a_vec))
            similarities.append((sim, anchor))
            
        # Sort by similarity
        similarities.sort(key=lambda x: x[0], reverse=True)
        subset = similarities[:top_n]
        
        # Aggregate local importance
        local_counts = {}
        for sim, anchor in subset:
            nodes = anchor.get("target_nodes", [])
            for node in nodes:
                # Similarity weighted count
                local_counts[node] = local_counts.get(node, 0) + sim
                
        # Normalize local weights (0.0 ~ 1.0)
        max_v = max(local_counts.values()) if local_counts else 1.0
        return {k: v/max_v for k, v in local_counts.items()}

domain_extractor = DomainSubsetExtractor()

class BayesianAdaptiveScorerV2:
    def __init__(self, global_likelihood_path='global_skill_likelihood.json'):
        self.global_importance = {}
        if os.path.exists(global_likelihood_path):
            with open(global_likelihood_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.global_importance = data.get("skill_importance", {})

    def get_expert_weights(self, target_skills, local_likelihood, alpha=0.3):
        """
        Bayesian Synthesis: Prior (Global) * Likelihood (Domain)
        """
        weights = {}
        for skill in target_skills:
            # 1. Global Prior (Background Noise)
            p_global = self.global_importance.get(skill, 0.5)
            
            # 2. Local Likelihood (Domain Expert Signal)
            p_local = local_likelihood.get(skill, 0.5)
            
            # 3. Combined Bayesian Weight
            # Give more weight to Domain (1-alpha)
            combined = (alpha * p_global) + ((1 - alpha) * p_local)
            weights[skill] = max(0.3, round(float(combined), 4))
            
        return weights

expert_scorer = BayesianAdaptiveScorerV2()

def calc_achievement_density_v9(raw_text):
    if not raw_text: return 0.0
    core_patterns = [r'\d+%', r'\d+억', r'\d+만', r'\d+명', r'\d+개', r'\d+년']
    tech_patterns = [r'특허', r'논문', r'제1저자', r'SCI', r'수상', r'\d+건']
    core_count = sum(len(re.findall(p, raw_text)) for p in core_patterns)
    tech_count = sum(len(re.findall(p, raw_text)) for p in tech_patterns)
    weighted_count = core_count + (tech_count * 0.5)
    density = weighted_count / (max(len(raw_text), 1) / 1000)
    return min(density / 5.0, 1.0)

def get_bm25_top_v9(query_text, top_k=100):
    import pickle
    index_path = 'bm25_index.pkl'
    if not os.path.exists(index_path): return {}
    with open(index_path, 'rb') as f:
        data = pickle.load(f)
        bm25 = data['bm25']
        ids = data['ids']
    def tokenize(text):
        tokens = re.findall(r'[가-힣]{2,}|[a-zA-Z]{2,}|\d+', text or '')
        return [t.lower() for t in tokens]
    tokenized_query = tokenize(query_text)
    scores = bm25.get_scores(tokenized_query)
    max_s = max(scores) if len(scores) > 0 and max(scores) > 0 else 1.0
    import numpy as np
    top_indices = np.argsort(scores)[::-1][:top_k]
    res = {}
    for idx in top_indices:
        s = scores[idx]
        if s > 0: res[str(ids[idx])] = s / max_s
    return res

def get_effective_gravity_v9(node, seniority="All"):
    field = UNIFIED_GRAVITY_FIELD.get(node, {})
    if seniority == "SENIOR" and node in SENIOR_EXPANDED_SYNERGY:
        field = field.copy()
        field["synergy_attracts"] = {**field.get("synergy_attracts", {}), **SENIOR_EXPANDED_SYNERGY[node]}
    return field

def calc_gravity_score_v9(candidate_nodes, query_nodes, seniority="All"):
    REPEL_MULTIPLIER = {"SENIOR": 0.5, "MIDDLE": 0.7, "JUNIOR": 0.9, "All": 0.7}
    repel_mult = REPEL_MULTIPLIER.get(seniority, 0.7)
    score = 0
    for node in query_nodes:
        field = get_effective_gravity_v9(node, seniority)
        core = field.get("core_attracts", {})
        for cnode, weight in core.items():
            if cnode in candidate_nodes: score += weight * 2.0
        synergy = field.get("synergy_attracts", {})
        for snode, weight in synergy.items():
            if snode in candidate_nodes: score += weight
        repels = field.get("repels", {})
        for rnode, weight in repels.items():
            if rnode in candidate_nodes: score += weight * repel_mult
    return score

def map_abbreviations_v9(query_str, conditions_list):
    expansion_map = {
        "IPO": ["Investor_Relations", "IPO_Preparation"],
        "IR": ["Investor_Relations"], "DFT": ["Design_for_Testability"],
        "RTL": ["RTL_Design"], "SoC": ["System_on_Chip"], "SAP": ["SAP_ERP"],
        "BI": ["Business_Intelligence"], "Tableau": ["Tableau"],
        "DevOps": ["DevOps", "CI_CD"], "SaaS": ["SaaS"],
        "Kotlin": ["Kotlin", "Android_Development"], "ASRS": ["Warehouse_Automation"]
    }
    # Ensure conditions_list is a list of dicts
    if not isinstance(conditions_list, list): return []
    
    for abbr, expansions in expansion_map.items():
        if re.search(r'\b' + re.escape(abbr) + r'\b', query_str, re.IGNORECASE):
            for exp in expansions:
                # Add check: c must be dict
                if not any(isinstance(c, dict) and c.get('skill') == exp for c in conditions_list):
                    conditions_list.append({"action": "MANAGED", "skill": exp, "is_mandatory": False, "source": "abbr_map"})
    return conditions_list

