import re

file_path = r'C:\Users\cazam\Downloads\이력서자동분석검색시스템\jd_compiler.py'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

patch_code = """
    # [Patch] 카테고리 매칭 처리 (Step 5-B)
    from ontology_graph import SKILL_CATEGORIES
    for cat_name, cat_skills in SKILL_CATEGORIES.items():
        if cat_name.lower() in lower_jd:
            for s in cat_skills:
                if s not in seen_nodes:
                    seen_nodes.add(s)
                    matched_nodes.append((s, cat_name.lower()))

"""

# Insert the patch right after seen_nodes = set()
content = re.sub(
    r'(seen_nodes\s*=\s*set\(\)\n)',
    r'\1' + patch_code,
    content,
    count=1
)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Patch applied to jd_compiler.py")
