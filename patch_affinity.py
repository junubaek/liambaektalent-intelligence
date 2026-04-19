import json
import re

NODE_AFFINITY_CODE = """
# ============================================================
# 1. ontology_graph.py 하단에 추가할 코드 (Node Affinity)
# ============================================================

NODE_AFFINITY = {
    "Product_Manager": {
        "strong_with": [
            ("Payment_and_Settlement_System", 0.9),
            ("Service_Planning", 0.85),
            ("Data_Pipeline_Construction", 0.8),
            ("Data_Analysis", 0.75),
        ],
        "preferred_action": "DESIGNED"
    },
    "Product_Owner": {
        "strong_with": [
            ("Service_Planning", 0.9),
            ("Data_Analysis", 0.8),
            ("Payment_and_Settlement_System", 0.75),
        ],
        "preferred_action": "DESIGNED"
    },
    "Financial_Planning_and_Analysis": {
        "strong_with": [
            ("Financial_Accounting", 0.9),
            ("Corporate_Strategic_Planning", 0.85),
            ("Management_Accounting", 0.8),
            ("Investor_Relations", 0.7),
        ],
        "preferred_action": "ANALYZED"
    },
    "Treasury_Management": {
        "strong_with": [
            ("Corporate_Funding", 0.9),
            ("FX_Dealing", 0.85),
            ("IPO_Preparation_and_Execution", 0.85),
            ("Financial_Accounting", 0.75),
        ],
        "preferred_action": "MANAGED"
    },
    "IPO_Preparation_and_Execution": {
        "strong_with": [
            ("Treasury_Management", 0.9),
            ("Investor_Relations", 0.9),
            ("Corporate_Funding", 0.85),
            ("Financial_Planning_and_Analysis", 0.8),
        ],
        "preferred_action": "DESIGNED"
    },
    "Backend_Architecture": {
        "strong_with": [
            ("MSA_Architecture", 0.9),
            ("Infrastructure_and_Cloud", 0.85),
            ("Data_Pipeline_Construction", 0.8),
        ],
        "preferred_action": "BUILT"
    },
    "Data_Engineering": {
        "strong_with": [
            ("Data_Pipeline_Construction", 0.9),
            ("Data_Warehouse_Architecture", 0.85),
            ("Infrastructure_and_Cloud", 0.8),
            ("Machine_Learning", 0.7),
        ],
        "preferred_action": "BUILT"
    },
    "Data_Analysis": {
        "strong_with": [
            ("Data_Engineering", 0.85),
            ("A_B_Testing", 0.8),
            ("Machine_Learning_for_Business", 0.75),
            ("Data_Visualization_and_Dashboarding", 0.7),
        ],
        "preferred_action": "ANALYZED"
    },
    "Machine_Learning": {
        "strong_with": [
            ("Data_Engineering", 0.85),
            ("MLOps", 0.85),
            ("Deep_Learning", 0.8),
            ("Data_Pipeline_Construction", 0.75),
        ],
        "preferred_action": "BUILT"
    },
    "Corporate_Strategic_Planning": {
        "strong_with": [
            ("Financial_Planning_and_Analysis", 0.85),
            ("Mergers_and_Acquisitions", 0.8),
            ("New_Business_Development", 0.8),
            ("Management_Consulting", 0.75),
        ],
        "preferred_action": "DESIGNED"
    },
    "Recruiting_and_Talent_Acquisition": {
        "strong_with": [
            ("HR_Strategic_Planning", 0.85),
            ("Organizational_Development", 0.8),
            ("Performance_and_Compensation_System", 0.75),
        ],
        "preferred_action": "MANAGED"
    },
}
"""

with open("ontology_graph.py", "a", encoding="utf-8") as f:
    f.write(NODE_AFFINITY_CODE)


JD_COMPILER_INJECT_CODE = """
from ontology_graph import NODE_AFFINITY

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
        if c["skill"] in NODE_AFFINITY
    ]

    if not detected_roles:
        return conditions

    affinity_added = []

    for role in detected_roles:
        affinity_data = NODE_AFFINITY[role]
        preferred_action = affinity_data["preferred_action"]

        for affinity_skill, weight in affinity_data["strong_with"]:
            if affinity_skill not in existing_skills:
                affinity_added.append({
                    "action": preferred_action,
                    "skill": affinity_skill,
                    "weight": weight,
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

"""

import sys

with open("jd_compiler.py", "r", encoding="utf-8") as f:
    jd_content = f.read()

# Append imports/functions below the current ontology_graph import
pattern1 = r"(from ontology_graph import CANONICAL_MAP)"
jd_content = re.sub(pattern1, r"\1" + "\n" + JD_COMPILER_INJECT_CODE, jd_content, count=1)

# Modify run_jd_compiler logic
new_run_jd_compiler = """def run_jd_compiler(jd_text: str):
    print("=" * 60)
    print(f"[JD Compiler] Input: {jd_text}")
    print("=" * 60)

    # Phase 1: Gemini 의도 추출
    extracted = parse_jd_to_json(jd_text)
    conds = extracted.get("conditions", [])
    min_years = extracted.get("min_years", 0)
    
    # 1-1. 다운그레이드 매핑 (그래프 단차 해소) 및 중복 제거
    conds = apply_downgrade_map(conds)
    extracted["conditions"] = conds
    
    print("\\n[Phase 1] Extracted Conditions:")
    print(json.dumps(extracted, indent=2, ensure_ascii=False))

    if not conds:
        print("조건을 추출하지 못했습니다.")
        return

    # Phase 1.5: NODE_AFFINITY 기반 자동 조건 주입
    conds = inject_node_affinity(conds)
    affinity_conds = [c for c in conds if c.get("source") == "auto_affinity"]
    if affinity_conds:
        print(f"\\n[Phase 1.5] Auto-Affinity Injected ({len(affinity_conds)}개):")
        for c in affinity_conds:
            print(f"  + {c['action']}:{c['skill']} (w:{c['weight']})")

    # Phase 2: TF-IDF 벡터 선추출
    print("\\n[Phase 2] Executing Vector Prefilter (TF-IDF)...")
    top_names = prefilter_candidates(jd_text, num_candidates=300)

    # Phase 3: Neo4j OPTIONAL MATCH 스코어링
    print(f"\\n[Phase 3] Executing Neo4j OPTIONAL MATCH Score calculation (min_years={min_years})...")
    results = opt_match_score(top_names, conds, min_years=min_years)

    # 3.5. History 가산점 부여
    history_bonuses = get_history_bonus_scores(jd_text)
    for c in results:
        for b_name, b_val in history_bonuses.items():
            if b_name and b_name in c['name']:
                c['total_score'] = round(c['total_score'] + b_val['score'], 2)
                c['history_msg'] = b_val['msg']
                break

    # 재정렬 (가산점 여부 등으로 순위 변동)
    results.sort(key=lambda x: x['total_score'], reverse=True)

    print("\\n" + "=" * 60)
    print("🏆 [FINAL RANKED CANDIDATES] (Top 20 | Pass Hurdle: 40%)")
    print("=" * 60)

    if not results:
        print("조건(40%)을 만족하는 최종 합격 후보자가 없습니다.")
        return

    for rank, c in enumerate(results[:20], start=1):
        auto_hits = [
            e for e in c.get("matched_edges", [])
            if any(
                a["skill"] in e
                for a in affinity_conds
            )
        ]
        print(f"{rank}. {c['name']} | Total Score: {c['total_score']}")
        if c.get("history_msg"):
            print(f"   {c['history_msg']}")
        print(f"   [+] Matched: {c['matched_edges']}")
        if auto_hits:
            print(f"   [~] Auto-Affinity Hit: {auto_hits}")
        if c.get("missing_edges"):
            print(f"   [-] Missing (for interview): {c['missing_edges']}")
        print("-" * 40)
"""

old_run_jd_pattern = r"def run_jd_compiler\(jd_text:\s*str\):.*?(?=def api_search_v8)"
jd_content = re.sub(old_run_jd_pattern, new_run_jd_compiler + "\n\n", jd_content, flags=re.DOTALL)

# Add it to api_search_v8 also as a bonus so the UI gets logic
api_pattern = r"(conds = apply_downgrade_map\(conds\))"
api_replacement = r"\1\n    conds = inject_node_affinity(conds)"
jd_content = re.sub(api_pattern, api_replacement, jd_content)

with open("jd_compiler.py", "w", encoding="utf-8") as f:
    f.write(jd_content)

print("Updated perfectly.")
