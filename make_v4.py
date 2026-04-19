import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

TO_REMOVE = [
    "AI Machine Learning Data Science",
    "Big Data Machine Learning Platform Architecture",
    "IoT Data Analytics AI/ML",
    "AI Semiconductor Hardware",
    "AI Semiconductor RCMS Research Fund Management",
    "Simulation Automation TMS",
    "OEM ExportCompliance MarketResearch",
    "Power System Analysis Grid Impact Assessment Database Design"
]

golden_data = []
with open('golden_dataset_v3.json', 'r', encoding='utf-8') as f:
    golden_data = json.load(f)

new_data = []
for entry in golden_data:
    q = entry.get('jd_query', '')
    # Remove if in TO_REMOVE or if it's the error JD
    if q in TO_REMOVE or "JD 본문이 제공되지 않아" in q:
        continue
    new_data.append(entry)

with open('golden_dataset_v4.json', 'w', encoding='utf-8') as f:
    json.dump(new_data, f, ensure_ascii=False, indent=4)

print(f"Original items: {len(golden_data)}")
print(f"Filtered items: {len(new_data)}")
print("Created golden_dataset_v4.json successfully!")
