import re

def deduplicate_canonical_map():
    with open('ontology_graph.py', 'r', encoding='utf-8') as f:
        lines = f.readlines()

    out_lines = []
    in_canonical_map = False
    seen_keys = set()
    deleted_count = 0

    key_pattern = re.compile(r'^\s*["\']([^"\']+)["\']\s*:')

    for line in lines:
        if 'CANONICAL_MAP' in line and '=' in line and '{' in line:
            in_canonical_map = True
            out_lines.append(line)
            continue
            
        if in_canonical_map:
            # End of dict
            if re.match(r'^\s*}\s*$', line):
                in_canonical_map = False
                out_lines.append(line)
                continue
                
            match = key_pattern.search(line)
            if match:
                key = match.group(1).strip()
                if key in seen_keys:
                    deleted_count += 1
                    print(f"Deleting duplicate key: {key}")
                    continue
                else:
                    seen_keys.add(key)
            
        out_lines.append(line)

    with open('ontology_graph.py', 'w', encoding='utf-8') as f:
        f.writelines(out_lines)

    print(f"Total deleted lines: {deleted_count}")

deduplicate_canonical_map()
