import codecs
import re

def fix_jd_c():
    with codecs.open('jd_compiler.py', 'r', 'utf-8') as f:
        content = f.read()

    # 1. Skip is_duplicate == 1
    # 2. Add education high school filter
    # 3. Clean up summary, current_company, sector mapping
    
    old_c_loop = '''            c_list = careers_list            

            # Robust company extraction
            current_comp = "̻"'''
    
    new_c_loop = '''            # 1. is_duplicate check
            if getattr(c, "is_duplicate", 0) == 1:
                continue

            c_list = careers_list            

            # Robust company extraction
            current_comp = "미상"'''

    if 'current_comp = "̻"' in content:
        content = content.replace('current_comp = "̻"', 'current_comp = "미상"')

    # We need to find exactly where to insert is_duplicate.
    # Let's replace the top of the candidate block:
    old_loop_str = '''        for c in parsed_cands:
            fb_data = json_cache_by_id.get(str(c.id))'''
    
    new_loop_str = '''        for c in parsed_cands:
            if getattr(c, "is_duplicate", 0) == 1:
                continue
            
            fb_data = json_cache_by_id.get(str(c.id))'''

    if old_loop_str in content:
        content = content.replace(old_loop_str, new_loop_str)

    # Clean up summary -> None
    # Clean up company -> "미상" -> UI filters it
    # Clean up sector -> "미분류" -> UI filters it
    
    with codecs.open('jd_compiler.py', 'w', 'utf-8') as f:
        f.write(content)

if __name__ == "__main__":
    fix_jd_c()
