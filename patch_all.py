import codecs
import re

def patch_compiler():
    with codecs.open('jd_compiler.py', 'r', 'utf-8') as f:
        content = f.read()

    # 1. Fix notion_url matching by stripping spaces
    old_fb = '''fb_data = json_cache.get(c.name_kr) or {}'''
    new_fb = '''fb_data = json_cache.get(c.name_kr) or {}
            if not fb_data and c.name_kr:
                c_clean = c.name_kr.replace(" ", "")
                for k, v in json_cache.items():
                    if k.replace(" ", "") == c_clean:
                        fb_data = v
                        break'''
    if old_fb in content:
        content = content.replace(old_fb, new_fb)

    # 2. Add max_graph_score, max_vector_score, top_skills, top_actions to payload
    old_payload_start = '''final_results.append(payload)'''
    new_payload_logics = '''
        from collections import Counter
        a_cnt = Counter(e['action'] for e in cand_edges)
        s_cnt = Counter(e['skill'] for e in cand_edges)
        payload['top_actions'] = [f"{k}({v})" for k,v in a_cnt.most_common(3)]
        payload['top_skills'] = [f"{k}({v})" for k,v in s_cnt.most_common(3)]
        final_results.append(payload)
'''
    if old_payload_start in content:
        content = content.replace(old_payload_start, new_payload_logics)

    # Calculate max scores after the loop
    old_sort = '''final_results.sort(key=lambda x: (x['_score'], x['total_edges']), reverse=True)'''
    new_sort = '''
    max_g = max([x['graph_score'] for x in final_results] + [1.0])
    max_v = max([x['vector_score'] for x in final_results] + [1.0])
    for r in final_results:
        r['max_graph_score'] = round(max_g, 4)
        r['max_vector_score'] = round(max_v, 4)
        
    final_results.sort(key=lambda x: (x['_score'], x['total_edges']), reverse=True)'''
    
    if old_sort in content:
        content = content.replace(old_sort, new_sort)

    with codecs.open('jd_compiler.py', 'w', 'utf-8') as f:
        f.write(content)

def patch_write_html():
    with codecs.open('write_html.py', 'r', 'utf-8') as f:
        content = f.read()

    # 2. Update Matched Nodes and Scores text interpolation
    # The string must exist in write_html.py EXACTLY. 
    # Graph Score UI:
    old_graph = '''<span class="text-indigo-600 text-[1.1rem] font-black">${c.graph_score || 0}</span>'''
    new_graph = '''<span class="text-indigo-600 text-[1.1rem] font-black">${c.graph_score || 0} <span class="text-slate-300 font-medium ml-1 text-[12px]">/ ${c.max_graph_score || 100}</span></span>'''
    if old_graph in content: content = content.replace(old_graph, new_graph)

    old_vector = '''<span class="text-blue-600 text-[1.1rem] font-black">${c.vector_score || 0}</span>'''
    new_vector = '''<span class="text-blue-600 text-[1.1rem] font-black">${c.vector_score || 0} <span class="text-slate-300 font-medium ml-1 text-[12px]">/ ${c.max_vector_score || 1.0}</span></span>'''
    
    if old_vector in content: content = content.replace(old_vector, new_vector)

    # Matched Nodes UI:
    old_matched = '''<span class="text-slate-800 leading-snug" style="font-size: 0.85rem; font-weight: 700; word-break: break-all;">${matchedEdges.join(', ')}</span>'''
    new_matched = '''<span class="text-slate-800 leading-snug" style="font-size: 0.85rem; font-weight: 700; word-break: break-all; margin-bottom: 4px; display: block;">Top Skills: ${(c.top_skills || []).join(', ')}</span>
                                                    <span class="text-slate-800 leading-snug" style="font-size: 0.85rem; font-weight: 700; word-break: break-all; color: #4b5563;">Top Actions: ${(c.top_actions || []).join(', ')}</span>'''
    
    if old_matched in content: content = content.replace(old_matched, new_matched)

    with codecs.open('write_html.py', 'w', 'utf-8') as f:
        f.write(content)

if __name__ == "__main__":
    patch_compiler()
    patch_write_html()
    print("Patched successfully")
