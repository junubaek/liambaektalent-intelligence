import sys
import os
import json

sys.stdout.reconfigure(encoding='utf-8')
sys.path.append(r'C:\Users\cazam\Downloads\이력서자동분석검색시스템')

from ontology_graph import CANONICAL_MAP, UNIFIED_GRAVITY_FIELD
from jd_compiler import parse_jd_to_json, deduplicate_conditions, apply_downgrade_map, inject_node_affinity

# [1] Simulate normalize_skill
def normalize_skill(skill_name: str) -> str:
    if skill_name in CANONICAL_MAP:
        return CANONICAL_MAP[skill_name]
    lower = skill_name.lower()
    for key, val in CANONICAL_MAP.items():
        if key.lower() == lower:
            return val
    return skill_name

raw_skills = [
    'NPU Kernel', 'NPU software stacks', 
    'Linux device driver', 'memory allocator',
    'execution scheduler', 'host runtime',
    'distributed inference systems', 'NVMe',
    'storage systems'
]

print("=== [1] normalize_skill() 변환 결과 ===")
for s in raw_skills:
    normalized = normalize_skill(s)
    print(f" {s} -> {normalized}")

# [2] Match with jd_target_skills
prompt = 'NPU 드라이버 커널 엔지니어 찾아줘'
print(f"\n=== [2] 쿼리 '{prompt}'의 파싱 및 jd_target_skills ===")
extracted = parse_jd_to_json(prompt)
conds = extracted.get("conditions", [])

# Map abbreviations
def map_abbreviations_to_conds(query_str, conditions_list):
    expansion_map = {
        "IPO": ["Investor_Relations", "IPO_Preparation"],
        "IR": ["Investor_Relations"], "DFT": ["Design_for_Testability"],
        "RTL": ["RTL_Design"], "SoC": ["System_on_Chip"], "SAP": ["SAP_ERP"],
        "BI": ["Business_Intelligence"], "Tableau": ["Tableau"],
        "DevOps": ["DevOps", "CI_CD"], "SaaS": ["SaaS"],
        "Kotlin": ["Kotlin", "Android_Development"], "ASRS": ["Warehouse_Automation"]
    }
    import re
    for abbr, expansions in expansion_map.items():
        if re.search(r'\b' + re.escape(abbr) + r'\b', query_str, re.IGNORECASE):
            for exp in expansions:
                if not any(c.get('skill') == exp for c in conditions_list):
                    conditions_list.append({"action": "MANAGED", "skill": exp, "is_mandatory": False, "source": "abbreviation_map"})
    return conditions_list

conds = map_abbreviations_to_conds(prompt, conds)
conds = deduplicate_conditions(conds)
conds = apply_downgrade_map(conds)
conds = inject_node_affinity(conds)

jd_target_skills = [c.get('skill', '') for c in conds if c.get('skill')]
print(f" jd_target_skills: {jd_target_skills}")

# Print intersection
normalized_skills = [normalize_skill(s) for s in raw_skills]
matched_skills = set(normalized_skills).intersection(set(jd_target_skills))
print(f" -> 전형준 스킬 중 쿼리와 직접 매칭되는 것: {list(matched_skills)}")

# [3] Search UNIFIED_GRAVITY_FIELD for core_attracts
print("\n=== [3] UNIFIED_GRAVITY_FIELD core_attracts 매핑 디버그 ===")
target_nodes = ['NPU_Kernel', 'Device_Driver', 'Linux_Kernel']
for target in target_nodes:
    print(f"\n--- '{target}' 노드의 core_attracts 포함 여부 ---")
    found = False
    for key, field in UNIFIED_GRAVITY_FIELD.items():
        core = field.get("core_attracts", {})
        if target in core:
            print(f" -> Found in '{key}' -> core_attracts | Weight: {core[target]}")
            found = True
    if not found:
        print(f" '{target}' is NOT in any gravity field's core_attracts.")
