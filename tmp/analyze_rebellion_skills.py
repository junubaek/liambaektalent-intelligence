import json
from collections import Counter

with open("temp_500_candidates.json", "r", encoding="utf-8-sig") as f:
    data = json.load(f)

skills = []

for c in data.get("results", []):
    props = c.get("properties", {})
    name = ""
    title_props = [v for k,v in props.items() if v.get("type") == "title"]
    if title_props and title_props[0].get("title"):
        name = title_props[0]["title"][0].get("plain_text", "")
            
    if "리벨리온" in name:
        # Extract from Sub Sectors
        sub_sectors = props.get("Sub Sectors", {}).get("multi_select", [])
        for s in sub_sectors:
            skills.append("S:" + s["name"])
            
        # Extract from Functional Patterns
        func_patterns = props.get("Functional Patterns", {}).get("multi_select", [])
        for s in func_patterns:
            skills.append("F:" + s["name"])

print("Top Sub Sectors:")
for s, count in Counter([x for x in skills if x.startswith("S:")]).most_common(20):
    print(f"{s}: {count}")

print("\nTop Functional Patterns:")
for s, count in Counter([x for x in skills if x.startswith("F:")]).most_common(30):
    print(f"{s}: {count}")
