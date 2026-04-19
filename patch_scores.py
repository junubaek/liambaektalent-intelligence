import codecs

def patch_scores():
    for f in ['frontend/index.html', 'script_3.js', 'write_html.py']:
        with codecs.open(f, 'r', 'utf-8') as file:
            c = file.read()
            
        o_g = '''<span class="text-indigo-600 text-[1.1rem] font-black">${c.graph_score || 0}</span>'''
        n_g = '''<span class="text-indigo-600 text-[1.1rem] font-black">${c.graph_score || 0} <span class="text-xs text-slate-400">/ ${c.max_graph_score || 0}</span></span>'''
        
        o_v = '''<span class="text-blue-600 text-[1.1rem] font-black">${c.vector_score || 0}</span>'''
        n_v = '''<span class="text-blue-600 text-[1.1rem] font-black">${c.vector_score || 0} <span class="text-xs text-slate-400">/ ${c.max_vector_score || 0}</span></span>'''
        
        if o_g in c: c = c.replace(o_g, n_g)
        if o_v in c: c = c.replace(o_v, n_v)
            
        with codecs.open(f, 'w', 'utf-8') as file:
            file.write(c)

if __name__ == "__main__":
    patch_scores()
