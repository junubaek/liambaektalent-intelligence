import codecs

def fix_jd_compiler():
    with codecs.open('jd_compiler.py', 'r', 'utf-8') as f:
        content = f.read()

    # The exact block to replace
    old_block = """            prof_sum = cache_ext.get("profile_summary", "") or fb_data.get("profile_summary", "")
            if not prof_sum or ("전화번호" in prof_sum and len(prof_sum) > 100):
                prof_sum = ""
"""
    new_block = """            prof_sum = cache_ext.get("profile_summary", "") or fb_data.get("profile_summary", "")
"""
    
    if old_block in content:
        content = content.replace(old_block, new_block)
        with codecs.open('jd_compiler.py', 'w', 'utf-8') as f:
            f.write(content)
        print("Fixed jd_compiler filter.")
    else:
        print("Block not found!")

if __name__ == "__main__":
    fix_jd_compiler()
