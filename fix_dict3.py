import re

def fix_by_tracking():
    with open('dup_results_utf8.txt', 'r', encoding='utf-8') as f:
        dup_lines = f.readlines()[1:]
        
    keys_to_track = set()
    for line in dup_lines:
        key_part = line.split(':')[0].strip()[1:-1]
        keys_to_track.add(key_part)
        
    with open('ontology_graph.py', 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    out_lines = []
    seen = set()
    deleted = 0
    in_dict = False
    
    for line in lines:
        if 'CANONICAL_MAP' in line and '=' in line and '{' in line:
            in_dict = True
            out_lines.append(line)
            continue
            
        if 'EDGES' in line and '=' in line and '{' in line:
            in_dict = False
            
        if in_dict:
            m = re.search(r'^\s*["\']([^"\']+)["\']\s*:', line)
            if m:
                key = m.group(1).strip()
                if key in keys_to_track:
                    if key in seen:
                        deleted += 1
                        continue # skip
                    else:
                        seen.add(key)
        
        out_lines.append(line)
        
    with open('ontology_graph.py', 'w', encoding='utf-8') as f:
        f.writelines(out_lines)
    print(f"Deleted {deleted} lines.")

fix_by_tracking()
