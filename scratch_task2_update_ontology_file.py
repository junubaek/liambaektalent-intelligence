import sys

sys.stdout.reconfigure(encoding='utf-8')
file_path = r"C:\Users\cazam\Downloads\이력서자동분석검색시스템\ontology_graph.py"

with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Modify CANONICAL_MAP
canonical_target = "CANONICAL_MAP: dict[str, str] = {"
npu_nodes = """
    # NPU Nodes
    "NPU kernel": "NPU_Kernel",
    "NPU 커널": "NPU_Kernel",
    "npu kernel": "NPU_Kernel",
    "NPU runtime": "NPU_Runtime",
    "NPU 런타임": "NPU_Runtime",
    "npu runtime": "NPU_Runtime",
    "NPU software stack": "NPU_Software_Stack",
    "NPU SW stack": "NPU_Software_Stack",
    "Tensix ISA": "Tenstorrent_ISA",
    "tenstorrent": "Tenstorrent_ISA",
    "tt-metal": "Tenstorrent_ISA",
    "RISC-V Vector": "RISC_V_Vector",
    "RISC-V VectorISA": "RISC_V_Vector",
    "rvv": "RISC_V_Vector",
    "vLLM": "LLM_Serving_Engine",
    "SGLang": "LLM_Serving_Engine",
    "TensorRT-LLM": "LLM_Serving_Engine",
    "llm serving engine": "LLM_Serving_Engine",
"""

if canonical_target in content:
    content = content.replace(canonical_target, canonical_target + npu_nodes, 1)
    print("Successfully added NPU nodes to CANONICAL_MAP")
else:
    print("Error: CANONICAL_MAP target not found!")

# 2. Modify EDGES
edges_target = "tuple[str, str, str, float]] = ["
npu_edges = """
    # NPU edges
    ("NPU_Kernel", "NPU_Design", "related_to", 2.0),
    ("NPU_Kernel", "Device_Driver", "related_to", 1.8),
    ("NPU_Runtime", "NPU_Design", "related_to", 1.8),
    ("NPU_Runtime", "LLM_Serving_Engine", "related_to", 1.5),
    ("Tenstorrent_ISA", "NPU_Kernel", "related_to", 2.0),
    ("RISC_V_Vector", "NPU_Kernel", "related_to", 1.8),
"""

if edges_target in content:
    content = content.replace(edges_target, edges_target + npu_edges, 1)
    print("Successfully added NPU edges to EDGES")
else:
    print("Error: EDGES target not found!")

# Write back to file
with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)

print("ontology_graph.py updated successfully.")
