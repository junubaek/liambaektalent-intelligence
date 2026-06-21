with open('frontend_v2/src/App.jsx', 'r', encoding='utf-8') as f:
    code = f.read()

import re
# Find function or UI elements for candidate details modal
print("=== Search React UI Sections in App.jsx ===")
lines = code.split('\n')
for idx, line in enumerate(lines):
    if 'modal' in line.lower() or 'card' in line.lower() or 'selectedcandidate' in line.lower() or 'tierbadge' in line.lower():
        print(f"Line {idx+1}: {line.strip()[:100]}")
