import sys

def fix_jd_compiler():
    with open("jd_compiler.py", "r", encoding="utf-8") as f:
        text = f.read()

    # 1. Fix parse_jd_to_json
    old_code_1 = """            affinity = NODE_AFFINITY.get(node, {})
            action = affinity.get("preferred_action", "MANAGED")"""
    new_code_1 = """            action = "MANAGED" # Default since UNIFIED_GRAVITY_FIELD structure lacks preferred_action"""
    text = text.replace(old_code_1, new_code_1)

    # 2. Fix inject_node_affinity
    old_code_2 = """def inject_node_affinity(conditions: list) -> list:
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
                existing_skills.add(affinity_skill)"""

    new_code_2 = """def inject_node_affinity(conditions: list) -> list:
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
                    "weight": weight,
                    "is_mandatory": False,
                    "source": "auto_affinity"
                })
                existing_skills.add(affinity_skill)"""
    
    text = text.replace(old_code_2, new_code_2)

    with open("jd_compiler.py", "w", encoding="utf-8") as f:
        f.write(text)

fix_jd_compiler()
print("Fixed jd_compiler.py")
