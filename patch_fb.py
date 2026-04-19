import codecs

def patch_fb_fallback():
    with codecs.open('jd_compiler.py', 'r', 'utf-8') as f:
        content = f.read()

    old_cache = '''for d in old_data:

                    if "name_kr" in d: json_cache[d["name_kr"]] = d

                    elif "name" in d: json_cache[d["name"]] = d'''
                    
    new_cache = '''json_cache_by_id = {}
                for d in old_data:
                    if "id" in d and d["id"]: 
                        json_cache_by_id[str(d["id"])] = d
                        json_cache_by_id[str(d["id"]).replace("-", "")] = d
                    if "name_kr" in d: json_cache[d["name_kr"]] = d
                    elif "name" in d: json_cache[d["name"]] = d'''
                    
    if old_cache in content:
        content = content.replace(old_cache, new_cache)

    old_fb = '''fb_data = json_cache.get(c.name_kr) or {}
            if not fb_data and c.name_kr:
                c_clean = c.name_kr.replace(" ", "")
                for k, v in json_cache.items():
                    if k.replace(" ", "") == c_clean:
                        fb_data = v
                        break'''

    new_fb = '''fb_data = json_cache_by_id.get(str(c.id)) or json_cache_by_id.get(str(c.id).replace("-", "")) or json_cache.get(c.name_kr) or {}
            if not fb_data and c.name_kr:
                c_clean = c.name_kr.replace(" ", "")
                for k, v in json_cache.items():
                    if c_clean in k.replace(" ", ""):
                        fb_data = v
                        break'''
                        
    if old_fb in content:
        content = content.replace(old_fb, new_fb)

    with codecs.open('jd_compiler.py', 'w', 'utf-8') as f:
        f.write(content)

if __name__ == "__main__":
    patch_fb_fallback()
    print("Patched FB")
