import codecs

def patch_frontend_details():
    with codecs.open('script_3.js', 'r', 'utf-8') as f:
        content = f.read()

    # The HTML string formatting
    
    # 1. Company HTML filtering
    old_co1 = '''<p class="flex items-center gap-1.5 font-bold text-slate-700 text-[13px] tracking-tight">'''
    old_co2 = '''<span class="font-extrabold text-[#7e69ab] mr-1.5 uppercase text-[9px]">Current / Latest :</span> ${company}</p>'''
    
    new_co = '''${(company && company !== '미상' && company !== '̻') ? `
                                            <p class="flex items-center gap-1.5 font-bold text-slate-700 text-[13px] tracking-tight">
                                                <span class="font-extrabold text-[#7e69ab] mr-1.5 uppercase text-[9px]">Current / Latest :</span> ${company}
                                            </p>` : ''}'''
                                            
    # Since exact matching spanning multiple lines with Korean characters in powershell fails a lot, let's use regex
    import re
    
    # Regex to find the <p class="flex items-center gap-1.5 font-bold text-slate-700 text-[13px] tracking-tight"> \s* <span class="font-extrabold text-[#7e69ab] mr-1.5 uppercase text-[9px]">Current / Latest :</span> ${company}</p>
    content = re.sub(
        r'<p class="flex items-center gap-1.5 font-bold text-slate-700 text-\[13px\] tracking-tight">\s*<span class="font-extrabold text-\[\#7e69ab\] mr-1.5 uppercase text-\[9px\]">Current / Latest :</span> \$\{company\}</p>',
        r"${(company && company !== '미상' && company !== '̻' && company !== ' ') ? `<p class=\"flex items-center gap-1.5 font-bold text-slate-700 text-[13px] tracking-tight\">\n<span class=\"font-extrabold text-[#7e69ab] mr-1.5 uppercase text-[9px]\">Current / Latest :</span> ${company}</p>` : ''}",
        content
    )
    
    content = re.sub(
        r'<p class="flex items-center gap-1.5 font-semibold text-slate-600 text-\[12px\] tracking-tight">\s*<span class="font-bold text-slate-400 mr-1.5 uppercase text-\[9px\]">Main Sector :</span> \$\{sectorVal\}</p>',
        r"${(sectorVal && sectorVal !== '미분류' && sectorVal !== '̺з' && sectorVal !== ' ') ? `<p class=\"flex items-center gap-1.5 font-semibold text-slate-600 text-[12px] tracking-tight\">\n<span class=\"font-bold text-slate-400 mr-1.5 uppercase text-[9px]\">Main Sector :</span> ${sectorVal}</p>` : ''}",
        content
    )
    
    with codecs.open('script_3.js', 'w', 'utf-8') as f:
        f.write(content)

if __name__ == "__main__":
    patch_frontend_details()
