import sys

sys.stdout.reconfigure(encoding='utf-8')
file_path = r"C:\Users\cazam\Downloads\이력서자동분석검색시스템\ontology_graph.py"

with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# Target for CANONICAL_MAP
target_line = '    # NPU Nodes'
additions = """
    "NPU Kernel": "NPU_Kernel",
    "NPU software stacks": "NPU_Software_Stack",
"""

if target_line in content:
    content = content.replace(target_line, target_line + additions, 1)
    print("Successfully added missing NPU aliases to CANONICAL_MAP")
else:
    print("Error: Target line not found!")

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)

print("ontology_graph.py updated.")
