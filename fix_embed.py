import os
content = open('embed_candidates.py', encoding='utf-8').read()
content = content.replace('[:12000]', '[:3500]')
content = content.replace('print(f"Error on batch', 'tqdm.write(f"Error on batch')
open('embed_candidates.py', 'w', encoding='utf-8').write(content)
print("Updated embed_candidates.py")
