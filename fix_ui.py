import re

def fix_jd_compiler():
    with open('jd_compiler.py', 'r', encoding='utf-8') as f:
        content = f.read()
        
    old_get_cand = '''"education_json": json.loads(c.education_json) if getattr(c, "education_json", None) else []

            })'''
    new_get_cand = '''"education_json": json.loads(c.education_json) if getattr(c, "education_json", None) else [],
                "notion_url": fb_data.get("notion_url", "#")
            })'''
    
    if old_get_cand in content:
        content = content.replace(old_get_cand, new_get_cand)
        
    old_payload = '''\'이메일\': c_info.get("email", "이메일 없음"),
            \'notion_url\': "#", # Can map real url if needed'''
            
    new_payload = '''\'이메일\': c_info.get("email", "이메일 없음"),
            \'birth_year\': c_info.get("birth_year", "생년 미상"),
            \'notion_url\': c_info.get("notion_url", "#"),'''
    
    if old_payload in content:
        content = content.replace(old_payload, new_payload)

    with open('jd_compiler.py', 'w', encoding='utf-8') as f:
        f.write(content)


def fix_script_3():
    with open('script_3.js', 'r', encoding='utf-8') as f:
        js = f.read()

    # 1. Update summary mapping to profile_summary
    old_summary = 'const summary = c["Experience Summary"] || \'정보 없음\';'
    new_summary = 'const summary = c.profile_summary || c["Experience Summary"] || \'정보 없음\';'
    if old_summary in js:
        js = js.replace(old_summary, new_summary)
        
    js = js.replace('const summary = c["Experience Summary"] || \' \';', new_summary)

    # 3. Add birth year and align contact info properly
    old_contact = '''<div class="flex items-center gap-10 text-[11px] font-bold text-slate-400 uppercase tracking-[0.1em] pt-2">
                                                <span class="flex items-center gap-2"><i data-lucide="phone" class="w-3.5 h-3.5 text-slate-300"></i> ${phone}</span>
                                                <span class="flex items-center gap-2"><i data-lucide="mail" class="w-3.5 h-3.5 text-slate-300"></i> ${email}</span>
                                            </div>'''
    
    new_contact = '''<div class="flex items-center gap-10 text-[11px] font-bold text-slate-400 uppercase tracking-[0.1em] pt-4">
                                                <span class="flex items-center gap-2"><i data-lucide="phone" class="w-3.5 h-3.5 text-slate-300"></i> ${phone}</span>
                                                <span class="flex items-center gap-2"><i data-lucide="mail" class="w-3.5 h-3.5 text-slate-300"></i> ${email}</span>
                                                <span class="flex items-center gap-2"><i data-lucide="calendar" class="w-3.5 h-3.5 text-slate-300"></i> ${c.birth_year ? c.birth_year + '년생' : '생년 미상'}</span>
                                            </div>'''
                                            
    if old_contact in js:
        js = js.replace(old_contact, new_contact)
        
    # Check if we need to parse birthYear
    old_vars = '''const missingEdges = c.missing_edges || [];'''
    new_vars = '''const missingEdges = c.missing_edges || [];
                        const birthYear = c.birth_year || '';'''
    if old_vars in js:
        js = js.replace(old_vars, new_vars)

    with open('script_3.js', 'w', encoding='utf-8') as f:
        f.write(js)

if __name__ == "__main__":
    fix_jd_compiler()
    fix_script_3()
    print("Fix OK")
