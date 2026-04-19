import codecs

def fix_jd_fb_data():
    with codecs.open('jd_compiler.py', 'r', 'utf-8') as f:
        content = f.read()

    # The careers extraction block
    old_career = '''            careers_list = cache_ext.get("parsed_career_json", [])
            if not careers_list:
                careers_list = fb_data.get("parsed_career_json", [])'''
                
    new_career = '''            careers_list = cache_ext.get("parsed_career_json", [])
            if not careers_list:
                careers_list = fb_data.get("parsed_career_json", [])
            if not careers_list and getattr(c, "careers_json", None):
                import json
                try: careers_list = json.loads(c.careers_json)
                except: pass'''

    if old_career in content:
        content = content.replace(old_career, new_career)
        with codecs.open('jd_compiler.py', 'w', 'utf-8') as f:
            f.write(content)
        print("Patched careers_json fallback.")
    else:
        print("Old career block not found!")

if __name__ == "__main__":
    fix_jd_fb_data()
