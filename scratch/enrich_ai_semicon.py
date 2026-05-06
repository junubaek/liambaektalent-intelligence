
import re
import sys
import os

# Ensure UTF-8 output
sys.stdout.reconfigure(encoding='utf-8')

ONTOLOGY_FILE = 'ontology_graph.py'

if not os.path.exists(ONTOLOGY_FILE):
    print(f"Error: {ONTOLOGY_FILE} not found.")
    sys.exit(1)

with open(ONTOLOGY_FILE, 'r', encoding='utf-8') as f:
    content = f.read()

edge_pattern = re.findall(r'\("([^"]+)",\s*"([^"]+)",\s*"([^"]+)",\s*([\d.]+)\)', content)
EXISTING = set()
for s, d, r, w in edge_pattern:
    EXISTING.add((s, d))
    EXISTING.add((d, s))

print(f'기존 엣지 수: {len(edge_pattern)}')

new_edges = []
added = set()

def add(src, dst, rel, weight):
    if (src, dst) not in EXISTING and (dst, src) not in EXISTING and (src, dst) not in added:
        new_edges.append((src, dst, rel, weight))
        added.add((src, dst))

# ════════════════════════════════════════════════════════
# LAYER 1 — 알고리즘 / 모델
# ════════════════════════════════════════════════════════
add("LLM_Engineering",    "LLM_Architecture",           "depends_on", 2.0)
add("LLM_Engineering",    "NLP_and_LLM_Optimization",   "related_to", 1.8)
add("LLM_Engineering",    "Natural_Language_Processing", "depends_on", 1.8)
add("LLM_Engineering",    "Deep_Learning",               "depends_on", 2.0)
add("LLM_Engineering",    "Model_Optimization",          "depends_on", 1.8)
add("LLM_Engineering",    "Distributed_Training_Inference", "related_to", 1.8)
add("LLM_Engineering",    "Frontier_AI_Research",        "related_to", 1.5)
add("LLM_Engineering",    "AI_Research",                 "related_to", 1.5)
add("LLM_Engineering",    "Generative_AI_and_3D_Vision", "related_to", 1.5)
add("LLM_Engineering",    "LLM_Inference",               "depends_on", 2.0)

add("LLM_Architecture",   "MoE",                         "part_of",    1.8)
add("LLM_Architecture",   "Model_Parallelism",           "depends_on", 2.0)
add("LLM_Architecture",   "KV_Cache_Optimization",       "depends_on", 2.0)
add("LLM_Architecture",   "Deep_Learning",               "depends_on", 2.0)
add("LLM_Architecture",   "NLP_and_LLM_Optimization",   "related_to", 1.8)
add("LLM_Architecture",   "PD_Disaggregation",           "related_to", 1.5)

add("MoE",                "Expert_Parallelism",          "depends_on", 2.0)
add("MoE",                "Model_Parallelism",           "related_to", 1.8)
add("MoE",                "Distributed_Training_Inference","depends_on",2.0)
add("Expert_Parallelism", "Model_Parallelism",           "similar_to", 1.8)
add("Expert_Parallelism", "Distributed_Training_Inference","depends_on",2.0)
add("Model_Parallelism",  "Distributed_Training_Inference","similar_to",1.8)
add("KV_Cache_Optimization","LLM_Serving",               "depends_on", 2.0)
add("KV_Cache_Optimization","PD_Disaggregation",         "related_to", 1.8)
add("PD_Disaggregation",  "LLM_Serving",                 "depends_on", 2.0)

add("LLM_Models",         "LLM_Architecture",            "part_of",    1.8)
add("LLM_Models",         "LLM_Engineering",             "part_of",    1.8)
add("LLM_Models",         "DeepSeek-R1",                 "part_of",    1.5)

add("Deep_Learning",      "Machine_Learning",            "depends_on", 1.8)
add("Deep_Learning",      "Natural_Language_Processing", "used_in",    1.5)
add("Deep_Learning",      "Recommendation_System",       "used_in",    1.5)
add("Deep_Learning_Modeling","Model_Optimization",       "depends_on", 1.8)
add("Deep_Learning_Modeling","Deep_Learning",            "part_of",    1.8)
add("Recommendation_System","Machine_Learning",          "depends_on", 1.8)
add("Recommendation_System","NLP_and_LLM_Optimization",  "related_to", 1.3)
add("AI_Research",        "Frontier_AI_Research",        "similar_to", 1.8)
add("AI_Research",        "Deep_Learning",               "depends_on", 1.8)
add("AI_Research",        "LLM_Engineering",             "related_to", 1.5)

# ════════════════════════════════════════════════════════
# LAYER 2 — SW 스택
# ════════════════════════════════════════════════════════
add("Firmware",           "Firmware_Engineering",        "similar_to", 2.0)
add("Firmware",           "Firmware_Development",        "similar_to", 1.8)
add("Firmware",           "Firmware_and_Embedded_Systems","similar_to",1.8)
add("Firmware",           "Embedded_Firmware",           "similar_to", 1.8)
add("Firmware_Development","Firmware_Engineering",       "similar_to", 1.8)
add("Firmware_Development","Embedded_Firmware",          "similar_to", 1.5)
add("Firmware_and_Embedded_Systems","Firmware_Engineering","similar_to",1.8)
add("Embedded_Firmware",  "Firmware_Engineering",        "similar_to", 1.8)

add("Compiler",           "AI_Compiler_and_System_Tools","similar_to", 1.8)
add("Compiler",           "Compute_Compiler_Library",    "related_to", 1.8)
add("Compiler",           "Embedded_System_and_Compiler_Optimization","related_to",1.5)
add("Compiler",           "NPU_Software_Stack",          "depends_on", 2.0)
add("Compiler",           "GPU_Driver",                  "related_to", 1.5)
add("AI_Compiler_and_System_Tools","NPU_Software_Stack", "depends_on", 2.0)
add("AI_Compiler_and_System_Tools","Compute_Compiler_Library","similar_to",1.8)
add("Compute_Compiler_Library","NPU_Software_Stack",     "depends_on", 1.8)
add("CUDA",               "GPGPU",                       "depends_on", 2.0)
add("CUDA",               "GPU_Driver",                  "depends_on", 2.0)
add("CUDA",               "GPU_Driver_and_Graphics_Pipeline","depends_on",2.0)
add("CUDA",               "LLM_Serving",                 "used_in",    1.5)
add("CUDA",               "Deep_Learning",               "used_in",    1.8)

add("GPU_Driver",         "GPU_Driver_and_Graphics_Pipeline","similar_to",1.8)
add("GPU_Driver",         "GPGPU",                       "depends_on", 2.0)
add("GPU_Driver",         "Sys_Software",                "part_of",    1.5)
add("GPU_Driver_and_Graphics_Pipeline","GPGPU",          "depends_on", 2.0)

add("NPU_Software_Stack", "NPU",                         "depends_on", 2.0)
add("NPU_Software_Stack", "Firmware_Engineering",        "related_to", 1.5)
add("NPU_Software_Stack", "Compiler",                    "depends_on", 1.8)
add("NPU_Software_Stack", "Sys_Software",                "part_of",    1.8)

add("TensorRT_LLM",       "LLM_Serving",                 "similar_to", 2.0)
add("TensorRT_LLM",       "vLLM",                        "similar_to", 1.8)
add("TensorRT_LLM",       "GPGPU",                       "depends_on", 2.0)
add("TensorRT_LLM",       "CUDA",                        "depends_on", 2.0)
add("TensorRT_LLM",       "LLM_Inference",               "depends_on", 2.0)
add("TensorRT_LLM",       "Model_Optimization",          "depends_on", 1.8)
add("vLLM",               "LLM_Inference",               "depends_on", 2.0)
add("vLLM",               "MLOps",                       "used_in",    1.5)
add("vLLM",               "CUDA",                        "depends_on", 1.8)
add("SGLang",             "LLM_Serving",                 "similar_to", 1.8)
add("SGLang",             "vLLM",                        "similar_to", 1.5)
add("SGLang",             "LLM_Inference",               "depends_on", 1.8)

add("ML_Pipeline",        "MLOps",                       "part_of",    1.8)
add("ML_Pipeline",        "Model_Serving",               "depends_on", 1.8)
add("ML_Pipeline",        "LLM_Inference",               "related_to", 1.5)
add("Model_Serving",      "LLM_Serving",                 "similar_to", 1.8)
add("Model_Serving",      "MLOps",                       "part_of",    1.8)
add("Model_Serving",      "vLLM",                        "used_in",    1.5)
add("LLM_Serving",        "LLM_Inference",               "depends_on", 1.8)
add("LLM_Serving_and_Data_Processing","LLM_Serving",     "similar_to", 1.8)
add("LLM_Serving_and_Data_Processing","LLM_Inference",   "depends_on", 1.8)

add("LLM_Inference",      "LLM_Engineering",             "depends_on", 2.0)
add("LLM_Serving",        "LLM_Engineering",             "depends_on", 1.8)

# ════════════════════════════════════════════════════════
# LAYER 5 — 시스템 / 칩 아키텍처
# ════════════════════════════════════════════════════════
add("HBM",                "High_Bandwidth_Memory",       "similar_to", 2.0)
add("HBM",                "HBM3",                        "similar_to", 1.8)
add("HBM",                "MemorySystem",                "part_of",    2.0)
add("HBM",                "DRAM_and_Memory_Architecture","related_to", 1.8)
add("HBM",                "NPU",                         "used_in",    2.0)
add("HBM",                "GPGPU",                       "used_in",    2.0)
add("HBM",                "PIM_and_AI_Memory_Architecture","related_to",1.8)
add("HBM",                "SoC",                         "used_in",    1.8)
add("HBM3",               "HBM",                         "similar_to", 1.8)
add("HBM3",               "MemorySystem",                "part_of",    1.8)
add("HBM3",               "High_Performance_Computing",  "used_in",    1.5)
add("High_Bandwidth_Memory","MemorySystem",              "similar_to", 2.0)
add("High_Bandwidth_Memory","DRAM_and_Memory_Architecture","similar_to",1.8)
add("High_Bandwidth_Memory","NPU",                       "used_in",    2.0)

add("AI_Accelerator",     "NPU",                         "similar_to", 1.8)
add("AI_Accelerator",     "GPGPU",                       "similar_to", 1.5)
add("AI_Accelerator",     "AI_Semiconductor_Architecture","part_of",   1.8)
add("AI_Accelerator",     "HBM",                         "depends_on", 1.8)
add("AI_Accelerator",     "Hardware_Architecture",       "part_of",    1.5)

add("NPU_Design",         "NPU",                         "similar_to", 2.0)
add("NPU_Design",         "AI_Semiconductor_Architecture","part_of",   1.8)
add("NPU_Design",         "SoC",                         "part_of",    1.8)
add("NPU_Design",         "Hardware_Architecture",       "depends_on", 2.0)
add("AI_Core",            "NPU",                         "part_of",    1.8)
add("AI_Core",            "NPU_Design",                  "similar_to", 1.8)
add("AI_Core",            "AI_Semiconductor_Architecture","part_of",   1.5)

add("GPU_Architecture",   "GPGPU",                       "part_of",    1.8)
add("GPU_Architecture",   "Hardware_Architecture",       "similar_to", 1.5)
add("GPU_Architecture",   "AI_Accelerator",              "related_to", 1.5)
add("GPU_Architecture",   "HBM",                         "depends_on", 1.8)

add("SmartNIC",           "High_Performance_Computing",  "used_in",    1.5)
add("SmartNIC",           "FPGA",                        "related_to", 1.5)
add("SmartNIC",           "NPU",                         "related_to", 1.3)

add("GPGPU",              "CUDA",                        "used_in",    2.0)
add("GPGPU",              "GPU_Driver",                  "depends_on", 2.0)
add("GPGPU",              "LLM_Serving",                 "used_in",    1.8)
add("GPGPU",              "MLOps",                       "used_in",    1.5)
add("SoC",                "NPU_Software_Stack",          "depends_on", 2.0)
add("SoC",                "Compiler",                    "depends_on", 1.8)

add("NPU",                "LLM_Inference",               "used_in",    2.0)
add("NPU",                "LLM_Engineering",             "used_in",    1.8)
add("GPGPU",              "Deep_Learning",               "used_in",    1.8)
add("GPGPU",              "LLM_Engineering",             "used_in",    1.8)
add("AI_Semiconductor_Architecture","LLM_Engineering",   "related_to", 1.5)
add("AI_Semiconductor_Architecture","NPU",               "part_of",    2.0)
add("AI_Semiconductor_Architecture","GPGPU",             "related_to", 1.5)
add("High_Performance_Computing","LLM_Engineering",      "used_in",    1.5)
add("High_Performance_Computing","Distributed_Training_Inference","used_in",1.8)

# ════════════════════════════════════════════════════════
# NODE_ALIASES 보강
# ════════════════════════════════════════════════════════
NEW_ALIASES = {
    "LLM_Engineering": [
        "LLM", "대형 언어 모델", "파운데이션 모델", "foundation model",
        "생성형 AI", "generative AI", "RAG", "파인튜닝", "fine-tuning",
        "LLM 엔지니어링", "프롬프트 엔지니어링", "prompt engineering",
        "LLM 개발", "언어모델", "GPT", "Claude", "Gemini",
        "RLHF", "instruction tuning", "LLM 파인튜닝",
    ],
    "LLM_Architecture": [
        "LLM 아키텍처", "Transformer", "트랜스포머",
        "Attention", "어텐션 메커니즘", "모델 아키텍처",
        "언어모델 설계", "LLM 구조",
    ],
    "MoE": [
        "Mixture of Experts", "MoE", "전문가 혼합",
        "sparse MoE", "dense MoE",
    ],
    "Model_Parallelism": [
        "모델 병렬화", "model parallelism", "텐서 병렬",
        "tensor parallel", "pipeline parallel", "파이프라인 병렬",
        "분산 학습", "distributed training",
    ],
    "Distributed_Training_Inference": [
        "분산 학습", "distributed training", "분산 추론",
        "대규모 학습", "클러스터 학습", "multi-node training",
        "학습 인프라", "training infrastructure",
    ],
    "KV_Cache_Optimization": [
        "KV cache", "KV 캐시", "캐시 최적화",
        "attention cache", "prefix caching",
    ],
    "PD_Disaggregation": [
        "PD disaggregation", "prefill-decode 분리",
        "prefill decode", "prefill 분리", "decode 분리",
    ],
    "Compiler": [
        "컴파일러", "compiler", "LLVM", "MLIR",
        "XLA", "TVM", "컴파일러 개발", "compiler engineer",
        "백엔드 컴파일러", "코드 생성",
    ],
    "AI_Compiler_and_System_Tools": [
        "AI 컴파일러", "AI compiler", "NPU 컴파일러",
        "신경망 컴파일러", "neural compiler",
        "AI 시스템 도구", "딥러닝 컴파일러",
    ],
    "CUDA": [
        "CUDA", "쿠다", "CUDA 프로그래밍",
        "GPU 프로그래밍", "CUDA kernel", "CUDA 커널",
        "GPU 병렬 프로그래밍", "CUDA C++",
    ],
    "TensorRT_LLM": [
        "TensorRT", "TensorRT-LLM", "TRT",
        "TensorRT 최적화", "TRT-LLM",
        "NVIDIA TensorRT", "텐서알티",
    ],
    "vLLM": [
        "vLLM", "PagedAttention", "paged attention",
        "vllm 서빙", "vLLM 배포",
    ],
    "NPU_Software_Stack": [
        "NPU 소프트웨어", "NPU SW", "NPU 스택",
        "NPU 드라이버", "NPU runtime",
        "NPU 런타임", "온디바이스 AI SW",
    ],
    "GPU_Driver": [
        "GPU 드라이버", "GPU driver", "디스플레이 드라이버",
        "그래픽 드라이버", "kernel mode driver",
    ],
    "Firmware_Engineering": [
        "펌웨어 엔지니어링", "firmware engineering",
        "펌웨어 개발", "firmware development",
        "임베디드 펌웨어", "embedded firmware",
        "BSP", "Board Support Package", "RTOS",
        "bare metal", "베어메탈",
    ],
    "Firmware": [
        "펌웨어", "firmware", "FW",
        "마이크로펌웨어", "micro firmware",
    ],
    "HBM": [
        "HBM", "High Bandwidth Memory", "고대역폭 메모리",
        "HBM2", "HBM2E", "HBM3", "HBM3E",
        "광대역 메모리",
    ],
    "High_Bandwidth_Memory": [
        "High Bandwidth Memory", "HBM", "고대역폭 메모리",
        "광대역폭 메모리", "HBM 아키텍처",
    ],
    "AI_Accelerator": [
        "AI 가속기", "AI accelerator", "AI chip",
        "AI 칩", "신경망 가속기", "딥러닝 가속기",
        "edge AI chip", "엣지 AI 칩",
    ],
    "NPU_Design": [
        "NPU 설계", "NPU design", "신경망 처리장치 설계",
        "AI 프로세서 설계", "NPU 아키텍처 설계",
    ],
    "GPU_Architecture": [
        "GPU 아키텍처", "GPU architecture",
        "그래픽 아키텍처", "GPU 마이크로아키텍처",
        "NVIDIA 아키텍처", "GPU 설계",
    ],
    "High_Performance_Computing": [
        "HPC", "고성능 컴퓨팅", "슈퍼컴퓨팅",
        "High Performance Computing", "클러스터 컴퓨팅",
        "병렬 컴퓨팅", "수퍼컴퓨터",
    ],
    "AI_Semiconductor_Architecture": [
        "AI 반도체 아키텍처", "AI 반도체 설계",
        "AI 칩 아키텍처", "인공지능 반도체",
        "AI SoC", "AI 프로세서", "뉴로모픽",
        "neuromorphic",
    ],
    "SmartNIC": [
        "SmartNIC", "스마트닉", "DPU",
        "Data Processing Unit", "네트워크 가속기",
        "네트워크 오프로딩", "network offload",
    ],
    "PIM_and_AI_Memory_Architecture": [
        "PIM", "Processing-in-Memory", "메모리 내 연산",
        "AI 메모리 아키텍처", "near-memory computing",
        "CXL", "CXL 메모리",
    ],
}

# ════════════════════════════════════════════════════════
# 파일 패치 1: 엣지 추가
# ════════════════════════════════════════════════════════
edge_lines = [
    '\n    # ══════════════════════════════════════════════',
    '    # AI+반도체 L1/L2/L5 레이어 엣지 보강 (2026-05-07)',
    '    # ══════════════════════════════════════════════',
]
for s, d, r, w in new_edges:
    w_str = str(int(w)) if w == int(w) else str(w)
    edge_lines.append(f'    ("{s}", "{d}", "{r}", {w_str}),')

edge_patch = '\n'.join(edge_lines)
last_edge_matches = list(re.finditer(r'\("[^"]+",\s*"[^"]+",\s*"[^"]+",\s*[\d.]+\),', content))
if last_edge_matches:
    pos = last_edge_matches[-1].end()
    content = content[:pos] + '\n' + edge_patch + content[pos:]

# ════════════════════════════════════════════════════════
# 파일 패치 2: NODE_ALIASES 보강
# ════════════════════════════════════════════════════════
alias_lines = [
    '',
    '    # ══ AI+반도체 L1/L2/L5 aliases (2026-05-07) ══',
]
for node, aliases in NEW_ALIASES.items():
    alias_lines.append(f'    "{node}": [')
    # Use EXISTING aliases to avoid duplicates if possible, or just overwrite/append
    # For now, following user's script to just append within the block
    for i, alias in enumerate(aliases):
        comma = ',' if i < len(aliases) - 1 else ''
        escaped = alias.replace('"', '\\"')
        alias_lines.append(f'        "{escaped}"{comma}')
    alias_lines.append('    ],')

if 'NODE_ALIASES' in content:
    na_start = content.find('NODE_ALIASES')
    na_end = content.find('\n}', na_start)
    if na_end != -1:
        alias_patch = '\n'.join(alias_lines)
        content = content[:na_end] + '\n' + alias_patch + content[na_end:]
        print('NODE_ALIASES 블록에 AI+반도체 항목 추가 완료')

with open(ONTOLOGY_FILE, 'w', encoding='utf-8') as f:
    f.write(content)

print(f'\n✅ 패치 완료')
print(f'   추가 엣지: {len(new_edges)}개')
print(f'   보강된 alias 노드: {len(NEW_ALIASES)}개')
