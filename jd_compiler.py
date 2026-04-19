from ontology_graph import UNIFIED_GRAVITY_FIELD

import os

import json

import uuid

from openai import OpenAI

from connectors.pinecone_api import PineconeClient

from vector_fallback import get_closest_node

from openai import OpenAI



# Secret Data for OpenAI/Pinecone

with open("secrets.json", "r") as f:

    secret_data = json.load(f)



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
        else:
            skill = edge
            action = "MANAGED"
            
        if skill in jd_target_skills:
            weight = ACTION_WEIGHTS.get(action, 1.0)
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

try:

    with open("secrets.json", "r", encoding="utf-8") as f:

        secrets = json.load(f)

        GENAI_KEY = secrets.get("GEMINI_API_KEY", "")

except Exception as e:

    logger.warning("secrets.json not found or invalid format.")

    GENAI_KEY = "PLEASE_SET_KEY"



client = genai.Client(api_key=GENAI_KEY)

MODEL_ID = 'gemini-2.5-flash'



def get_history_bonus_scores(jd_text: str, top_k: int = 50) -> Dict[str, Dict]:

    try:

        with open("secrets.json", "r", encoding="utf-8") as f:

            secret_data = json.load(f)

            

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

    for k in sorted_keys:

        k_lower = k.lower()

        if k_lower in lower_jd:

            # 영문 단어인 경우 (예: PO) 부분문자열 오진 방지 (예: IPO에서 PO 매칭 방지)

            if re.search(r'[a-z]', k_lower):

                pattern = r'(?<![a-z])' + re.escape(k_lower) + r'(?![a-z])'

                if not re.search(pattern, lower_jd):

                    continue

                    

            v = CANONICAL_MAP[k]

            if v not in seen_nodes:

                seen_nodes.add(v)

                matched_nodes.append((v, k_lower))

                if len(matched_nodes) >= 4:

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

                driver = GraphDatabase.driver('bolt://127.0.0.1:7687', auth=('neo4j', 'toss1234'))

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

                    

        rows = db.query(Candidate).outerjoin(ParsingCache).all()

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

        return {}



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
        driver = GraphDatabase.driver("bolt://127.0.0.1:7687", auth=("neo4j", "toss1234"))
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
            conn = sqlite3.connect('candidates.db')
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
    
    with open("secrets.json", "r", encoding="utf-8") as f:
        secrets = json.load(f)
    api_key = secrets.get("OPENAI_API_KEY") or secrets.get("openai_api_key")
    
    client = OpenAI(api_key=api_key)
    
    # [Phase 1: Vector Search (Tower 1)]
    emb_res = client.embeddings.create(input=[prompt], model="text-embedding-3-small")
    query_vector = emb_res.data[0].embedding
    
    vector_results = []
    id_to_name = {}
    
    driver = GraphDatabase.driver("bolt://127.0.0.1:7687", auth=("neo4j", "toss1234"))
    try:
        with driver.session() as session:
            q_vec = """
            CALL db.index.vector.queryNodes('candidate_embedding', 75, $queryVector)
            YIELD node AS c, score
            RETURN c.id AS id, coalesce(c.name_kr, c.name) AS name, score
            """
            res = session.run(q_vec, queryVector=query_vector)
            for r in res:
                cid = str(r["id"]) if r["id"] else r["name"]
                if cid:
                    vector_results.append({'id': cid, 'name': r['name'], 'score': r['score']})
                    id_to_name[cid] = r['name']
    except Exception as e:
        logger.error(f"[Tower 1] Vector error: {e}")
        
    logger.info(f"[Tower 1] Extracted Top-30 via Pinecone.")

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
            edges_map = {str(r["id"]): r["skills"] for r in res_e}
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
    
    return {'matched': dedup[:10], 'total': len(dedup), "is_category_search": is_category_search}

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

def api_search_v9(prompt: str, session_id: str = None) -> list:
    import math
    import time
    from connectors.openai_api import OpenAIClient
    from neo4j import GraphDatabase
    driver = GraphDatabase.driver("bolt://127.0.0.1:7687", auth=("neo4j", "toss1234"))
    
    st = time.time()
    logger.info(f"\n\n[V9.0 Chunk-Level API Search] Payload: {prompt}")
    
    openai = OpenAIClient(secret_data.get("OPENAI_API_KEY", ""))
    system_prompt = "주어진 사용자의 직무/스킬 요구사항을 분석하여 1536차원 벡터 검색에 유리하게 연관 스킬 키워드들로 확장된 영어 명사 위주의 검색 쿼리로 변환해."
    expanded_query_text = openai.get_chat_completion(system_prompt, prompt)
    if not expanded_query_text: expanded_query_text = prompt
    
    query_vector = openai.embed_content(expanded_query_text)
    if not query_vector:
        logger.error("[V9.0] Embedding generation failed.")
        return []
        
    import re
    raw_keywords = set(re.findall(r'[a-zA-Z0-9가-힣]+', prompt))
    canonical_targets = normalize_query_with_map(list(raw_keywords))

    with driver.session() as session:
        # STAGE 1: Vector Search across Experience Chunks
        vector_query = """
        CALL db.index.vector.queryNodes('chunk_embeddings', 150, $query_vector)
        YIELD node AS chunk, score AS vector_score
        MATCH (c:Candidate)-[:HAS_EXPERIENCE]->(chunk)
        RETURN c.id AS candidate_id, c.name_kr AS name, chunk.id AS chunk_id, 
               chunk.company_name AS company_name, chunk.end_date AS end_date, vector_score
        """
        stage1_results = session.run(vector_query, query_vector=query_vector).data()

        if not stage1_results:
            return []

        chunk_ids = [res['chunk_id'] for res in stage1_results]

        # STAGE 2: Graph Scoring per Chunk
        graph_query = """
        MATCH (chunk:Experience_Chunk)-[r]->(s:Skill)
        WHERE chunk.id IN $chunk_ids AND s.name IN $canonical_targets
        RETURN chunk.id AS chunk_id, collect({skill: s.name, action: type(r)}) AS edges, 
               COUNT { (chunk)-[]->() } AS total_edges
        """
        stage2_results = session.run(graph_query, chunk_ids=chunk_ids, canonical_targets=canonical_targets).data()

    # Organize Graph results mapped to chunks
    graph_map = {res['chunk_id']: res for res in stage2_results}

    # Group by Candidate, keeping the "Best Match Chunk"
    candidates_best_chunk = {}

    for v_res in stage1_results:
        cid = v_res['candidate_id']
        chk_id = v_res['chunk_id']
        company = v_res.get('company_name', 'Unknown')
        end_date = v_res.get('end_date', '')
        v_score = v_res['vector_score']
        
        g_res = graph_map.get(chk_id, {})
        edges = g_res.get('edges', [])
        total_edges = g_res.get('total_edges', 0)
        
        raw_graph_score = sum(ACTION_WEIGHTS.get(edge['action'], 1.0) for edge in edges)
        final_graph_score = math.log(max(raw_graph_score, 0) + 1)
        
        # Calculate Final Chunk Score
        recency_mult = calculate_recency_multiplier(end_date)
        
        # User Formula: Final_Chunk_Score = (Graph_Action_Weight * 0.6) + (Vector_Score * 0.3) + (Edge_Bonus)
        # Using final_graph_score for Graph_Action_Weight
        edge_bonus = min(total_edges * 0.01, 1.0) # Bonus capping
        final_chunk_score = ((final_graph_score * 0.6) + (v_score * 0.3) + edge_bonus) * recency_mult
        
        chunk_obj = {
            "chunk_id": chk_id,
            "company": company,
            "end_date": end_date,
            "recency_mult": recency_mult,
            "graph_score": final_graph_score,
            "vector_score": v_score,
            "final_score": final_chunk_score,
            "matched_edges": [e['skill'] for e in edges],
            "total_edges": total_edges
        }

        # Update candidate if this chunk is better
        if cid not in candidates_best_chunk:
            candidates_best_chunk[cid] = {"id": cid, "name": v_res['name'], "best_chunk": chunk_obj}
        elif final_chunk_score > candidates_best_chunk[cid]["best_chunk"]["final_score"]:
            candidates_best_chunk[cid]["best_chunk"] = chunk_obj

    # Sort Candidates by their Best Chunk's Final Score
    sorted_results = sorted(
        candidates_best_chunk.values(),
        key=lambda x: (x["best_chunk"]["final_score"], x["best_chunk"]["vector_score"]),
        reverse=True
    )
    
    # Format to traditional API response
    final_output = []
    for cand in sorted_results[:10]:
        best = cand["best_chunk"]
        
        # UX Explainability String
        explain = f"[{best['company']}]에서 최근 역량 인정 ({best['end_date']} 종료). "
        if best["recency_mult"] > 1.0: explain += "(최신경력 부스팅 적용🚀)"
        elif best["recency_mult"] < 1.0: explain += "(과거경력 패널티⬇️)"
        
        final_output.append({
            "name": cand["name"],
            "hash": cand["id"],
            "score": best["final_score"],
            "best_company": best["company"],
            "explain_reason": explain,
            "graph_score": best["graph_score"],
            "vector_score": best["vector_score"],
            "matched_edges": best["matched_edges"],
            "total_edges": best["total_edges"],
            "raw_text": "",
            "summary": "V9.0 Chunk-level Evaluated."
        })
        
    return final_output
