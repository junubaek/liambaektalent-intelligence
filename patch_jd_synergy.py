import re

file_path = r'C:\Users\cazam\Downloads\이력서자동분석검색시스템\jd_compiler.py'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update calculate_gravity_fusion_score signature and logic
old_def = "def calculate_gravity_fusion_score(candidate_edges, target_node, graph_score, vector_score=0.0):"
new_def = "def calculate_gravity_fusion_score(candidate_edges, target_node, graph_score, vector_score=0.0, is_category_search=False):"
content = content.replace(old_def, new_def)

# Find where synergy_bonus is used to calculate total_bonus and insert a reset
old_calc = "    total_bonus = core_bonus + (synergy_bonus * 1.5)"
new_calc = """    if is_category_search:
        synergy_bonus = 0.0

    total_bonus = core_bonus + (synergy_bonus * 1.5)"""
content = content.replace(old_calc, new_calc)

# 2. Update parse_jd_to_json
# Find our previous patch:
old_patch = """    # [Patch] 카테고리 매칭 처리 (Step 5-B)
    from ontology_graph import SKILL_CATEGORIES
    for cat_name, cat_skills in SKILL_CATEGORIES.items():
        if cat_name.lower() in lower_jd:
            for s in cat_skills:
                if s not in seen_nodes:
                    seen_nodes.add(s)
                    matched_nodes.append((s, cat_name.lower()))"""

new_patch = """    # [Patch] 카테고리 매칭 처리 (Step 5-B) + Category Flag
    from ontology_graph import SKILL_CATEGORIES
    is_category_search = False
    for cat_name, cat_skills in SKILL_CATEGORIES.items():
        if cat_name.lower() in lower_jd:
            is_category_search = True
            for s in cat_skills:
                if s not in seen_nodes:
                    seen_nodes.add(s)
                    matched_nodes.append((s, cat_name.lower()))"""
content = content.replace(old_patch, new_patch)

# Wait, we must make sure all returns from parse_jd_to_json include 'is_category_search'
# Let's replace returns.
content = re.sub(
    r'return \{"min_years": min_years, "conditions": conditions\}',
    r'return {"min_years": min_years, "conditions": conditions, "is_category_search": is_category_search}',
    content
)
content = re.sub(
    r'return \{"min_years": min_years, "conditions": \[\], "error": ([^\}]+)\}',
    r'return {"min_years": min_years, "conditions": [], "error": \1, "is_category_search": False}',
    content
)

# 3. Update api_search_v8
old_extract = """    extracted = parse_jd_to_json(prompt)
    conds = extracted.get("conditions", [])"""
new_extract = """    extracted = parse_jd_to_json(prompt)
    conds = extracted.get("conditions", [])
    is_category_search = extracted.get("is_category_search", False)"""
content = content.replace(old_extract, new_extract)

old_call = "real_score = calculate_gravity_fusion_score(cand_edges, target_node, base_g + freeform_synergy_bonus, base_v)"
new_call = "real_score = calculate_gravity_fusion_score(cand_edges, target_node, base_g + freeform_synergy_bonus, base_v, is_category_search)"
content = content.replace(old_call, new_call)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Patch for disabling synergy on category search successfully applied.")
