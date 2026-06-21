import sys

sys.stdout.reconfigure(encoding='utf-8')
file_path = r"C:\Users\cazam\Downloads\이력서자동분석검색시스템\ontology_graph.py"

with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# Target line
target_line = '    # NPU Nodes'
additions = """
    "커널": "Linux_Kernel",
    "커널 드라이버": "Device_Driver", 
    "드라이버": "Device_Driver",
    "드라이버 개발": "Device_Driver",
    "NPU 드라이버": "NPU_Kernel",
    "NPU 커널": "NPU_Kernel",
    "런타임": "NPU_Runtime",
    "NPU 런타임": "NPU_Runtime",
    "커널 개발": "Linux_Kernel",
    "디바이스 드라이버": "Device_Driver",
"""

if target_line in content:
    content = content.replace(target_line, target_line + additions, 1)
    print("Successfully added Korean NPU/kernel/driver single aliases to CANONICAL_MAP")
else:
    print("Error: Target line not found!")

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)

print("ontology_graph.py updated successfully.")
