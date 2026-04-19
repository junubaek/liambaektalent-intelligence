import os
for root, dirs, files in os.walk('.'):
    for f in files:
        if f.endswith('.py'):
            pth = os.path.join(root, f)
            try:
                content = open(pth, encoding='utf-8').read()
                if 'eval_results' in content or 'evaluate' in content.lower():
                    print('FOUND_E in:', pth)
            except Exception as e:
                pass
