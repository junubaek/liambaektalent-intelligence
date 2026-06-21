import sys
import os

sys.stdout.reconfigure(encoding='utf-8')

files_to_modify = [
    r"C:\Users\cazam\Downloads\이력서자동분석검색시스템\jd_compiler.py",
    r"C:\Users\cazam\Downloads\이력서자동분석검색시스템\jd_compiler_v8_1_final.py"
]

normalization_function = """            def normalize_skill(skill_name: str) -> str:
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
                edges_map[str(r["id"])] = normalized_skills"""

for file_path in files_to_modify:
    if not os.path.exists(file_path):
        print(f"Error: {file_path} not found.")
        continue
        
    print(f"Modifying: {file_path}...")
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
        
    # [api_search_v8]
    target_v8 = """            res_e = session.run(q_edge, ids=combined_ids)
            edges_map = {str(r["id"]): r["skills"] for r in res_e}"""
            
    if target_v8 in content:
        content = content.replace(target_v8, "            res_e = session.run(q_edge, ids=combined_ids)\n" + normalization_function, 1)
        print("  - Successfully replaced in api_search_v8")
    else:
        print("  - Warning: target_v8 not found!")

    # [api_search_v9]
    target_v9 = """            res_e = session.run(\"\"\"
                MATCH (c:Candidate)-[r]->(s:Skill)
                WHERE (c.id IN $ids OR c.name_kr IN $ids) AND type(r) <> 'USED_AS_TEMP'
                RETURN coalesce(c.id, c.name_kr) AS id, collect(DISTINCT {skill: s.name, action: type(r)}) AS skills
            \"\"\", ids=combined_ids)
            edges_map = {str(r["id"]): r["skills"] for r in res_e}"""
            
    if target_v9 in content:
        replacement_v9 = """            res_e = session.run(\"\"\"
                MATCH (c:Candidate)-[r]->(s:Skill)
                WHERE (c.id IN $ids OR c.name_kr IN $ids) AND type(r) <> 'USED_AS_TEMP'
                RETURN coalesce(c.id, c.name_kr) AS id, collect(DISTINCT {skill: s.name, action: type(r)}) AS skills
            \"\"\", ids=combined_ids)\n\n""" + normalization_function
            
        content = content.replace(target_v9, replacement_v9, 1)
        print("  - Successfully replaced in api_search_v9")
    else:
        print("  - Warning: target_v9 not found!")

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)

print("Modification complete.")
