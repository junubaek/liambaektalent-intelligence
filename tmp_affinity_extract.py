import sys
sys.path.append(r"c:\Users\cazam\Downloads\이력서자동분석검색시스템")
from ontology_graph import CANONICAL_MAP

# Group by canonical node
affinity_groups = {}
for alias, canonical in CANONICAL_MAP.items():
    if canonical not in affinity_groups:
        affinity_groups[canonical] = set()
    affinity_groups[canonical].add(alias)

md_lines = ["# Talent OS Node Affinity Configuration\n"]
md_lines.append("This document outlines the current node affinity (aliases -> canonical node) mappings used in the Talent Intelligence Graph.\n")

md_lines.append(f"**Total Canonical Nodes:** {len(affinity_groups)}\n")
md_lines.append(f"**Total Aliases Mapped:** {len(CANONICAL_MAP)}\n\n")

md_lines.append("| Canonical Node (Affinity Target) | Mapped Aliases (Synonyms/Keywords) | Count |")
md_lines.append("|---|---|---|")

# Sort alphabetically by Canonical Node
for canonical in sorted(affinity_groups.keys()):
    aliases = sorted(list(affinity_groups[canonical]))
    # remove the canonical name itself if it exists in aliases for cleaner look, or just show it
    aliases_str = ", ".join(aliases)
    count = len(aliases)
    md_lines.append(f"| **{canonical}** | {aliases_str} | {count} |")

# Write to artifact dir directly or Local Dir
output_path = r"c:\Users\cazam\.gemini\antigravity\brain\ac0c6b2a-94de-4147-b593-1f3c5c401168\artifacts\node_affinity_report.md"
import os
os.makedirs(os.path.dirname(output_path), exist_ok=True)
with open(output_path, "w", encoding="utf-8") as f:
    f.write("\n".join(md_lines))

print(f"Report generated successfully with {len(affinity_groups)} canonical nodes.")
