import re

# 1. READ jd_compiler.py
with open("jd_compiler.py", "r", encoding="utf-8") as f:
    jd_content = f.read()

# EXTRACT UNIFIED_GRAVITY_FIELD using regex
gravity_field_pattern = re.compile(r"(UNIFIED_GRAVITY_FIELD\s*=\s*\{.*?^\})", re.MULTILINE | re.DOTALL)
m = gravity_field_pattern.search(jd_content)

if not m:
    print("Could not find UNIFIED_GRAVITY_FIELD in jd_compiler.py")
    # Actually wait, maybe it's just a dict that ends with a single brace. Let's find index manually
    start_idx = jd_content.find("UNIFIED_GRAVITY_FIELD = {")
    end_idx = jd_content.find("}\n\n", start_idx) + 1
    if start_idx != -1 and end_idx != 0:
        gravity_block = jd_content[start_idx:end_idx]
    else:
        print("Manual search failed, exit.")
        exit(1)
else:
    gravity_block = m.group(1)

# DELETE from jd_compiler.py and add import
new_jd_content = jd_content.replace(gravity_block, "")

import_stmt = "from ontology_graph import UNIFIED_GRAVITY_FIELD"
if import_stmt not in new_jd_content:
    new_jd_content = import_stmt + "\n" + new_jd_content

with open("jd_compiler.py", "w", encoding="utf-8") as f:
    f.write(new_jd_content)

print("Updated jd_compiler.py")

# 2. READ ontology_graph.py and DELETE NODE_AFFINITY
with open("ontology_graph.py", "r", encoding="utf-8") as f:
    ont_content = f.read()

node_affinity_start = ont_content.find("NODE_AFFINITY = {")
if node_affinity_start != -1:
    ont_content = ont_content[:node_affinity_start]
    
# APPEND UNIFIED_GRAVITY_FIELD 
ont_content += "\n\n" + gravity_block + "\n"

with open("ontology_graph.py", "w", encoding="utf-8") as f:
    f.write(ont_content)
    
print("Updated ontology_graph.py")
