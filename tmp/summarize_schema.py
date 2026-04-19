import json
import os

with open("tmp_schema.json", "r", encoding="utf-8") as f:
    schema = json.load(f)

md_lines = []
md_lines.append("# Notion Candidate Database Schema\n")
md_lines.append("이 문서는 현재 Talent Intelligence OS에 연동된 핵심 Notion 데이터베이스의 컬럼(Property) 구조를 정리한 백서입니다.\n")
md_lines.append("## Properties Overview\n")

for prop_name, prop_data in sorted(schema.items(), key=lambda x: x[0]):
    ptype = prop_data.get("type", "unknown")
    md_lines.append(f"### `{prop_name}`")
    md_lines.append(f"- **Type**: `{ptype}`")
    
    if ptype == "multi_select":
        options = prop_data.get("multi_select", {}).get("options", [])
        md_lines.append(f"- **Options Count**: {len(options)}")
        if options:
            sample = [o["name"] for o in options[:5]]
            md_lines.append(f"- **Sample Options**: {', '.join(sample)} ...")
    elif ptype == "select":
        options = prop_data.get("select", {}).get("options", [])
        md_lines.append(f"- **Options Count**: {len(options)}")
        if options:
            sample = [o["name"] for o in options]
            md_lines.append(f"- **Options**: {', '.join(sample)}")
    md_lines.append("")

artifact_path = r"C:\Users\cazam\.gemini\antigravity\brain\bf9cf191-3e7a-4628-8914-c6b8c894b562\notion_database_schema_report.md"
with open(artifact_path, "w", encoding="utf-8") as f:
    f.write("\n".join(md_lines))

print(f"Generated Markdown report to {artifact_path}")
