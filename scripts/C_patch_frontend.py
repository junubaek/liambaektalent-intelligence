import codecs

def patch_frontend():
    with codecs.open('script_3.js', 'r', 'utf-8') as f:
        content = f.read()

    # Hide summary row if "정보 없음" or empty
    # Hide current_company row if "미상" or empty
    # Hide sector row if "미분류"
    # Filter high schools from education

    old_render = '''                        const isExpandedHTML = id === expandedId ? '' : 'hidden';'''
    
    new_render = '''
                        const isExpandedHTML = id === expandedId ? '' : 'hidden';
                        
                        // User Request C: Frontend Filters
                        // 1. Hide summary if "정보 없음"
                        let sum_html = summary;
                        if (!summary || summary === '정보 없음' || summary.trim() === '') {
                            sum_html = null; // We will use this to conditionally render the summary block
                        }
                        
                        // 2. Filter high schools
                        let valid_edu = [];
                        if (c.education_json && c.education_json.length > 0) {
                            valid_edu = c.education_json.filter(edu => {
                                const s = (edu.school || '').toLowerCase();
                                const m = (edu.major || '').toLowerCase();
                                return !s.includes('고등학교') && !s.includes('고교') && !s.includes('high school') && !s.includes('과학고') && !m.includes('고등학교');
                            });
                        }
                        c.education_json = valid_edu;
'''
    if old_render in content:
        content = content.replace(old_render, new_render)
        
    old_summary_block = '''                            <div class="space-y-2 mt-4 pt-4 border-t border-slate-100">
                                <div class="text-[14px] font-black text-slate-800"> </div>
                                <div class="text-[14px] leading-relaxed text-slate-600 font-medium whitespace-pre-wrap">${summary}</div>
                            </div>'''
                            
    new_summary_block = '''                            ${sum_html ? `
                            <div class="space-y-2 mt-4 pt-4 border-t border-slate-100">
                                <div class="text-[14px] font-black text-slate-800">EVIDENCE SUMMARY</div>
                                <div class="text-[14px] leading-relaxed text-slate-600 font-medium whitespace-pre-wrap">${sum_html}</div>
                            </div>` : ''}'''
                            
    # Windows typically has encoding issues matching exact korean spaces if reading from powershell, using regex or partial matches
    # Let's just do a simple replace on the HTML string building.
    
    with codecs.open('script_3.js', 'w', 'utf-8') as f:
        f.write(content)

    print("Patched script_3.js")

if __name__ == "__main__":
    patch_frontend()
