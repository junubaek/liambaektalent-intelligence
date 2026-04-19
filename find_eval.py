import os
for root, dirs, files in os.walk('.'):
    for f in files:
        if f.endswith('.py'):
            pth = os.path.join(root, f)
            try:
                content = open(pth, encoding='utf-8').read()
                if 'run_evaluation_pipeline' in content or 'evaluate_engine' in content:
                    print('FOUND in:', pth)
            except Exception as e:
                pass
