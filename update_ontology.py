import re

with open('ontology_graph.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Add to CANONICAL_MAP
new_canonical = """    # === LLM Engineering Additions ===
    "LLM 엔지니어": "LLM_Engineering",
    "LLM Engineer": "LLM_Engineering",
    "RAG 엔지니어": "LLM_Engineering",
    "RAG 개발": "LLM_Engineering",
    "Fine-tuning": "LLM_Engineering",
    "파인튜닝": "LLM_Engineering",
    "프롬프트 엔지니어링": "LLM_Engineering",
    "LangChain": "LLM_Engineering",
    "LlamaIndex": "LLM_Engineering",

"""

# Insert right after `CANONICAL_MAP: dict[str, str] = {` 
if '"LLM 엔지니어"' not in content:
    content = content.replace(
        "CANONICAL_MAP: dict[str, str] = {",
        "CANONICAL_MAP: dict[str, str] = {\n" + new_canonical,
        1
    )

# 2. Add to EDGES
new_edges = """    # LLM Engineering
    ("LLM_Engineering", "Natural_Language_Processing", "part_of", 1.5),
    ("LLM_Engineering", "MLOps", "related_to", 1.0),
    ("LLM_Engineering", "Backend_Engineering", "related_to", 1.0),
    ("LLM_Engineering", "AI_Engineering", "part_of", 1.5),

"""

if '("LLM_Engineering", "Natural_Language_Processing", "part_of", 1.5)' not in content:
    content = content.replace(
        "EDGES = [",
        "EDGES = [\n" + new_edges,
        1
    )

with open('ontology_graph.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Ontology Graph updated with LLM_Engineering!")
