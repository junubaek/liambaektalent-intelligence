import sys, os
sys.stdout.reconfigure(encoding='utf-8')

for fname in ['ontology_vectors.pkl', 'ontology_node_vectors.pkl']:
    if os.path.exists(fname):
        import pickle
        with open(fname, 'rb') as f:
            data = pickle.load(f)
        dtype = type(data).__name__
        size = len(data) if hasattr(data, '__len__') else '?'
        if isinstance(data, dict):
            sample_keys = list(data.keys())[:3]
        else:
            sample_keys = str(data)[:100]
        print(f'{fname} 존재: type={dtype}, size={size}, sample_keys={sample_keys}')
    else:
        print(f'{fname} 없음')
