import os
import time
from datetime import datetime

d = r'C:\Users\cazam\Downloads\02_resume 전처리'
now = time.time()
stats = {'today': 0, 'last_3d': 0, 'last_7d': 0, 'last_30d': 0, 'older': 0, 'total': 0}

for r, _, fs in os.walk(d):
    for f in fs:
        if f.startswith('~$') or not f.lower().endswith(('.pdf', '.docx', '.doc')):
            continue
        stats['total'] += 1
        filepath = os.path.join(r, f)
        t = os.path.getmtime(filepath)
        diff = (now - t) / 86400
        
        if diff <= 1:
            stats['today'] += 1
        elif diff <= 3:
            stats['last_3d'] += 1
        elif diff <= 7:
            stats['last_7d'] += 1
        elif diff <= 30:
            stats['last_30d'] += 1
        else:
            stats['older'] += 1

print("File Modification Date Stats for:", d)
for k, v in stats.items():
    print(f"{k}: {v}")
