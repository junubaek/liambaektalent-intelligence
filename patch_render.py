import codecs
import re

files_to_patch = ['frontend/index.html', 'script_3.js', 'write_html.py']

def patch_file(filepath):
    with codecs.open(filepath, 'r', 'utf-8') as f:
        content = f.read()
        
    old_school = '''${edu.schoolName}</span>, ${edu.major}'''
    new_school = '''${edu.schoolName || edu.school || '학교명 없음'}</span>, ${edu.major || ''}'''
    if old_school in content:
        content = content.replace(old_school, new_school)
        
    old_matched = '''<span class="text-slate-800 leading-snug" style="font-size: 0.85rem; font-weight: 700; word-break: break-all;">${matchedEdges.join(', ')}</span>'''
    new_matched = '''<span class="text-slate-800 leading-snug" style="font-size: 0.85rem; font-weight: 700; word-break: break-all; margin-bottom: 4px; display: block;">Top Skills: ${(c.top_skills || []).join(', ')}</span>
                                                    <span class="text-slate-800 leading-snug" style="font-size: 0.85rem; font-weight: 700; word-break: break-all; color: #4b5563;">Top Actions: ${(c.top_actions || []).join(', ')}</span>'''
    
    if old_matched in content:
        content = content.replace(old_matched, new_matched)

    with codecs.open(filepath, 'w', 'utf-8') as f:
        f.write(content)

for fp in files_to_patch:
    try:
        patch_file(fp)
    except:
        pass
        
print("Patched rendering logic")
