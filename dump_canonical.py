import sys
import os
from ontology_graph import CANONICAL_MAP

total_rules = len(CANONICAL_MAP)
unique_skills = set(CANONICAL_MAP.values())

with open("canonical_map_dump.md", "w", encoding="utf-8") as f:
    f.write(f"# CANONICAL MAP 현황 ({total_rules} 규칙 -> {len(unique_skills)} 고유 스킬)\n\n")
    
    # Target Skills Analysis
    f.write("## 🎯 타겟 필터링 스킬 검색 결과\n")
    
    targets = ["자금", "treasury", "fx", "funding", "ipo"]
    for t in targets:
        f.write(f"### '{t}' 관련 규칙\n")
        matches = {k: v for k, v in CANONICAL_MAP.items() if t in k.lower() or t in v.lower()}
        if not matches:
            f.write("> 텅 빔\n\n")
        else:
            for k, v in matches.items():
                f.write(f"- `{k}` ➔ **{v}**\n")
        f.write("\n")
        
    f.write("## 📋 전체 CANONICAL MAP (알파벳순 고유 스킬 기준 그룹화)\n")
    
    # Group by Canonical Skill
    grouped = {}
    for k, v in CANONICAL_MAP.items():
        grouped.setdefault(v, []).append(k)
        
    for standard_skill in sorted(grouped.keys()):
        synonyms = ", ".join([f"`{x}`" for x in grouped[standard_skill]])
        f.write(f"### {standard_skill}\n")
        f.write(f"- 동의어/유의어: {synonyms}\n\n")

print(f"Total Rules: {total_rules}")
print(f"Unique Skills: {len(unique_skills)}")
