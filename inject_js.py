import codecs

with codecs.open('script_3.js', 'r', 'utf-8') as f:
    js = f.read()

with codecs.open('frontend/index.html', 'r', 'utf-8') as f:
    html = f.read()

s_idx = html.find('const MAIN_SECTORS =')
e_idx = html.find('document.addEventListener(\\'DOMContentLoaded\\', init);')

if s_idx == -1 or e_idx == -1:
    print(f"Error finding markers. s_idx: {s_idx}, e_idx: {e_idx}")
    exit(1)

js_s_idx = js.find('const MAIN_SECTORS =')
js_e_idx = js.find('window.onload = init;')

if js_s_idx == -1 or js_e_idx == -1:
    print(f"Error finding JS markers. s_idx: {js_s_idx}, e_idx: {js_e_idx}")
    exit(1)

new_html = html[:s_idx] + js[js_s_idx:js_e_idx] + "document.addEventListener('DOMContentLoaded', init);\n    " + html[e_idx + len("document.addEventListener('DOMContentLoaded', init);"):]

with codecs.open('frontend/index.html', 'w', 'utf-8') as f:
    f.write(new_html)

print("Injected successfully!")
