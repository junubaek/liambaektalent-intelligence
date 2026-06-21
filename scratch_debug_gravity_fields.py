import sys
import os

sys.stdout.reconfigure(encoding='utf-8')
sys.path.append(r'C:\Users\cazam\Downloads\이력서자동분석검색시스템')

from ontology_graph import UNIFIED_GRAVITY_FIELD

print("=== [3] NPU_Kernel Gravity Field Mapping Debug ===")
print("Searching for 'NPU_Kernel' in UNIFIED_GRAVITY_FIELD attracts/repels...")

found = False
for key, field in UNIFIED_GRAVITY_FIELD.items():
    core = field.get("core_attracts", {})
    synergy = field.get("synergy_attracts", {})
    repels = field.get("repels", {})
    
    if "NPU_Kernel" in core:
        print(f" -> Found in '{key}' -> core_attracts | Weight: {core['NPU_Kernel']}")
        found = True
    if "NPU_Kernel" in synergy:
        print(f" -> Found in '{key}' -> synergy_attracts | Weight: {synergy['NPU_Kernel']}")
        found = True
    if "NPU_Kernel" in repels:
        print(f" -> Found in '{key}' -> repels | Weight: {repels['NPU_Kernel']}")
        found = True

if not found:
    print("NPU_Kernel was not found in any gravity field's core_attracts/synergy_attracts/repels!")
