import codecs
import re

def patch_backend():
    with codecs.open('jd_compiler.py', 'r', 'utf-8') as f:
        content = f.read()

        
    old_loop = '''for r in final_results:
        r['max_graph_score'] = round(max_g, 4)
        r['max_vector_score'] = round(max_v, 4)
        
    final_results.sort(key=lambda x: (x['_score'], x['total_edges']), reverse=True)'''

    new_loop = '''for r in final_results:
        r['max_graph_score'] = round(max_g, 4)
        r['max_vector_score'] = round(max_v, 4)
        import re
        cname = r['name_kr'] or ''
        cname = re.sub(r'\\[.*?\\]', '', cname)
        cname = re.sub(r'\\(.*?\\)', '', cname)
        cname = cname.replace('이력서', '').replace('사본', '').replace('복사본', '').replace('사', '').strip()
        r['name_kr'] = cname if cname else r['name_kr']
        
    final_results.sort(key=lambda x: (x['_score'], x['total_edges']), reverse=True)
    
    # Deduplicate by pure name
    seen_names = set()
    dedup = []
    for r in final_results:
        pure = re.sub(r'[^가-힣a-zA-Z]', '', r['name_kr'])
        if pure not in seen_names:
            seen_names.add(pure)
            dedup.append(r)
    final_results = dedup'''
    
    if old_loop in content:
        content = content.replace(old_loop, new_loop)
        
    with codecs.open('jd_compiler.py', 'w', 'utf-8') as f:
        f.write(content)

if __name__ == "__main__":
    patch_backend()
