with open('frontend_v2/src/App.jsx', 'r', encoding='utf-8') as f:
    code = f.read()

import re
print("=== Headers/Labels in App.jsx ===")
labels = re.findall(r'className=".*?".*?>\s*([^<>\n\t{]{2,30})\s*<', code)
unique_labels = list(set([l.strip() for l in labels if l.strip()]))
for label in sorted(unique_labels)[:30]:
    print("Label:", label)
