import re

file_path = r'C:\Users\cazam\Downloads\이력서자동분석검색시스템\ontology_graph.py'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Replace specific lines
# "NPU": "AI_Semiconductor_Architecture" -> "NPU": "NPU"
content = re.sub(r'"NPU":\s*"AI_Semiconductor_Architecture"', r'"NPU": "NPU"', content)
content = re.sub(r"'NPU':\s*'AI_Semiconductor_Architecture'", r"'NPU': 'NPU'", content)

# "LLM": "Natural_Language_Processing" -> "LLM": "LLM"
# LLM might map to Natural_Language_Processing or LLM_Engineering? Let's replace any mapping of "LLM"
content = re.sub(r'"LLM":\s*"[^"]+"', r'"LLM": "LLM"', content)
content = re.sub(r"'LLM':\s*'[^']+'", r"'LLM': 'LLM'", content)

# "네트워크": "Network_Engineer" -> "네트워크": "Networking"
content = re.sub(r'"네트워크":\s*"[^"]+"', r'"네트워크": "Networking"', content)
content = re.sub(r"'네트워크':\s*'[^']+'", r"'네트워크': 'Networking'", content)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Replacement complete.")
