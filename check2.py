import sys
sys.path.append('c:/Users/cazam/Downloads/이력서자동분석검색시스템')

def main():
    try:
        from ontology_graph import CANONICAL_MAP, EDGES
    except Exception as e:
        print("Import error", e)
        return

    from collections import Counter
    # check keys
    keys = list(CANONICAL_MAP.keys())
    c = Counter(keys)
    for k, v in c.items():
        if v > 1:
            print("Dup key:", k)

    # check edge pairs
    pairs = [tuple(sorted([s, t])) for s, t, r, w in EDGES]
    cp = Counter(pairs)
    for k, v in cp.items():
        if v > 1:
            print("Dup pair:", k, "count:", v)

if __name__ == '__main__':
    main()
