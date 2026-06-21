import os
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

print("Updating UNIFIED_GRAVITY_FIELD in ontology_graph.py...")

with open('ontology_graph.py', 'r', encoding='utf-8') as f:
    code = f.read()

new_fields = """
    'Network_on_Chip': {
        'sector': 'Semiconductor_SoC',
        'core_attracts': {
            'SoC': 0.9,
            'Chiplet_Architecture': 0.85,
            'ASIC': 0.8,
            'ARM_Architecture': 0.7,
            'RISC_V': 0.6,
        },
        'synergy_attracts': {
            'High_Performance_Computing': 0.5,
            'GPU_Acceleration': 0.4,
        },
        'repels': []
    },

    'Chiplet_Architecture': {
        'sector': 'Semiconductor_SoC',
        'core_attracts': {
            'SoC': 0.9,
            'Network_on_Chip': 0.85,
            'ASIC': 0.8,
            'DRAM_and_Memory_Architecture': 0.6,
        },
        'synergy_attracts': {
            'High_Bandwidth_Memory': 0.5,
            'PIM_and_AI_Memory_Architecture': 0.4,
        },
        'repels': []
    },

    'RISC_V': {
        'sector': 'Semiconductor_NPU',
        'core_attracts': {
            'NPU': 0.9,
            'NPU_Kernel': 0.85,
            'Digital_Signal_Processing': 0.8,
            'Embedded_Firmware': 0.7,
            'ASIC': 0.65,
        },
        'synergy_attracts': {
            'AI_Compiler_and_System_Tools': 0.5,
            'CUDA': 0.4,
        },
        'repels': []
    },
"""

# Insert these new gravity field entries right after "UNIFIED_GRAVITY_FIELD = {"
target_str = "UNIFIED_GRAVITY_FIELD = {"
idx = code.find(target_str)
if idx != -1:
    insert_pos = idx + len(target_str)
    code = code[:insert_pos] + new_fields + code[insert_pos:]
    with open('ontology_graph.py', 'w', encoding='utf-8') as f:
        f.write(code)
    print("UNIFIED_GRAVITY_FIELD updated successfully in ontology_graph.py.")
else:
    print("UNIFIED_GRAVITY_FIELD definition not found in ontology_graph.py!")
