import json

with open("golden_dataset_v3.json", "r", encoding="utf-8") as f:
    data = json.load(f)

remove_queries = [
    "AI Machine Learning Data Science",
    "Big Data Machine Learning Platform Architecture",
    "IoT Data Analytics AI/ML",
    "AI Semiconductor Hardware",
    "AI Semiconductor RCMS Research Fund Management",
    "Simulation Automation TMS",
    "OEM ExportCompliance MarketResearch",
    "Power System Analysis Grid Impact Assessment Database Design",
    "JD 본문이 제공되지 않아..."
]

new_data = [item for item in data if not any(item.get('jd_query', '').startswith(q) for q in remove_queries)]

print(f"Original items: {len(data)}, new items: {len(new_data)}")

with open("golden_dataset_v4.json", "w", encoding="utf-8") as f:
    json.dump(new_data, f, indent=4, ensure_ascii=False)
