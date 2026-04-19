import os
for root, dirs, files in os.walk('.'):
    for f in files:
        if f.endswith('.py'):
            pth = os.path.join(root, f)
            try:
                content = open(pth, encoding='utf-8').read().upper()
                if 'NDCG' in content or 'HIT IN TOP' in content:
                    print('FOUND in:', pth)
            except Exception as e:
                pass
