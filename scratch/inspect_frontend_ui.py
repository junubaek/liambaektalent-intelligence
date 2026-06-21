with open('frontend/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

import re
print("=== Titles and UI Headers in frontend/index.html ===")
headers = re.findall(r'<h[1-4].*?>(.*?)</h[1-4]>', html, re.DOTALL)
for h in headers[:15]:
    print("Header:", h.strip())
