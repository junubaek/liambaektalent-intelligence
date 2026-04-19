import codecs

def patch_frontend():
    for filepath in ['frontend/index.html', 'script_3.js', 'write_html.py']:
        with codecs.open(filepath, 'r', 'utf-8') as f:
            content = f.read()

        old_btn = '''<a href="${notion_url}" target="_blank" class="flex items-center gap-3 px-10 py-4.5 bg-black text-white rounded-full text-[11px] font-black uppercase tracking-widest hover:scale-105 transition-all shadow-xl shadow-black/10">'''
        new_btn = '''<a href="${c.google_drive_url || notion_url || '#'}" target="_blank" class="flex items-center gap-3 px-10 py-4.5 bg-black text-white rounded-full text-[11px] font-black uppercase tracking-widest hover:scale-105 transition-all shadow-xl shadow-black/10">'''
        
        if old_btn in content:
            content = content.replace(old_btn, new_btn)

        with codecs.open(filepath, 'w', 'utf-8') as f:
            f.write(content)

if __name__ == "__main__":
    patch_frontend()
    print("Patched UI linking")
