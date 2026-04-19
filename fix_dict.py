import re

def fix_canonical_map():
    with open('ontology_graph.py', 'r', encoding='utf-8') as f:
        lines = f.readlines()

    out_lines = []
    in_canonical_map = False
    brace_level = 0
    seen_keys = set()
    deleted_lines = 0

    key_pattern = re.compile(r'^\s*["\']([^"\']+)["\']\s*:')

    for line in lines:
        if 'CANONICAL_MAP' in line and '=' in line and '{' in line:
            in_canonical_map = True
            brace_level = line.count('{') - line.count('}')
            out_lines.append(line)
            continue
            
        if in_canonical_map:
            brace_level += line.count('{') - line.count('}')
            
            match = key_pattern.search(line)
            if match:
                key = match.group(1).strip()
                if key in seen_keys:
                    deleted_lines += 1
                    continue
                else:
                    seen_keys.add(key)
            
            if brace_level == 0:
                in_canonical_map = False
        
        out_lines.append(line)

    with open('ontology_graph.py', 'w', encoding='utf-8') as f:
        f.writelines(out_lines)
    print(f"Deleted {deleted_lines} lines.")

fix_canonical_map()
