import sys
sys.path.append('.')
from backend.search_engine_v6 import search_candidates_v6

req = type('Req', (object,), {
    "prompt": """토스에서 Financial System Manager를 뽑아.
PM, PO 라고 생각하면 되고, 정산/회계 쪽을 다뤄보신 분을 원해
개발쪽 경험이 짧게 있으면 좋고, 최소 6년 차 이상 경험자를 모시려고 해.

이 포지션은 재무회계 경력자를 뽑는게 아니라, 정산 데이터 라인을 구축하고 분석해서 설계하는 포지션이야.

말하자면 정산 System PM 인거지. 정산 시스템을 기획/구축해주실 분을 뽑는거야""",
    "required_skills": [],
    "preferred_skills": [],
    "seniority": "Senior"
})()

from app.engine.neo4j_snapper import Neo4jCandidateSnapper
from app.graph_engine.core_graph import SkillGraphEngine
from app.engine.resume_snap import CandidateSnapper

graph = SkillGraphEngine()
snapper = CandidateSnapper(graph)
from utils.gemini_nlu import extract_search_intent

parsed = extract_search_intent(req.prompt, req.required_skills, req.preferred_skills)
extraction_input_req = req.required_skills + parsed.get("sub_sectors", [])
extraction_input_pref = req.preferred_skills + parsed.get("pattern_keywords", [])

required_nodes = snapper.extract_and_map_skills(extraction_input_req)
preferred_nodes = snapper.extract_and_map_skills(extraction_input_pref)
exclude_nodes = snapper.extract_and_map_skills(parsed.get("exclude", []))

combined_nodes = {}
for node, w in required_nodes.items():
    combined_nodes[node] = {"weight": max(4.0, combined_nodes.get(node, {}).get("weight", 0)), "is_core": True}
for node, w in preferred_nodes.items():
    combined_nodes[node] = {"weight": max(2.0, combined_nodes.get(node, {}).get("weight", 0)), "is_core": combined_nodes.get(node, {}).get("is_core", False)}
for node, w in exclude_nodes.items():
    combined_nodes[node] = {"weight": -1.0, "is_core": False}

jd_nodes_list = []
for node, info in combined_nodes.items():
    jd_nodes_list.append({"name": node, "weight": info["weight"], "is_core": info["is_core"]})

raw_for_tendency = {n: i["weight"] for n, i in combined_nodes.items()}
jd_tendency = snapper.get_tendency_vector(raw_for_tendency)

uri = "neo4j+ssc://2c78ff2f.databases.neo4j.io"
user = "neo4j"
password = "sUdocj6IJEdIWCPNE6qzJq7kCdynS6EjSuBeKJtcye4"
neo_engine = Neo4jCandidateSnapper(uri, user, password)

kim_id = "[토스인슈어런스] 김완희(Financial Systems Manager)부문.pdf"
results = neo_engine.search_candidates(jd_tendency, jd_nodes_list, candidate_ids=[kim_id])
print("Kim Wan-hee Results:", results)
neo_engine.close()
