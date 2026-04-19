import json
import codecs
from collections import Counter

with codecs.open("temp_500_candidates.json", "r", encoding="utf-8-sig") as f:
    data = json.load(f)

skills = []
for c in data.get('results', [])[:500]:
    props = c.get('properties', {})
    for prop_name, prop_data in props.items():
        prop_type = prop_data.get('type')
        if any(k in prop_name.lower() for k in ['skill', 'tech', 'stack', '분야', '경험', '역량']):
            if prop_type == 'multi_select':
                skills.extend([item['name'] for item in prop_data.get('multi_select', [])])
            elif prop_type == 'rich_text':
                text_content = "".join([t.get('plain_text', '') for t in prop_data.get('rich_text', [])])
                if ',' in text_content:
                    skills.extend([x.strip() for x in text_content.split(',') if x.strip()])

counter = Counter([s for s in skills if s and len(s) > 1])
print("=== TOP 70 SKILLS IN RESUMES ===")
for s, c in counter.most_common(70):
    print(f"{s}: {c}")
