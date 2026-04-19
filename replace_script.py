import re

with open('c:/Users/cazam/Downloads/이력서자동분석검색시스템/frontend_v2/src/App.jsx', 'r', encoding='utf-8') as f:
    text = f.read()

start_str = '  const renderCareerDetails = (candidate, summary) => {'
end_str = '  const renderAdminConsole = () => ('

if start_str in text and end_str in text:
    before = text.split(start_str)[0]
    after = end_str + text.split(end_str)[1]
    
    replacement = '''  const renderCareerDetails = (candidate, summary) => {
    let edges = candidate.matched_edges ? candidate.matched_edges.slice(0, 3) : [];
    let actions = candidate.matched_actions ? candidate.matched_actions.slice(0, 2) : [];
    let matchStr = [...edges, ...actions].join(', ');
    if (!matchStr) matchStr = '직무 핵심 키워드 매칭 진행';

    return (
        <div className="pt-8 animate-fade-in border-t border-gray-100 mt-6 relative z-10 cursor-default" onClick={(e) => e.stopPropagation()}>
            <div className="flex justify-between items-start mb-8 tracking-tighter">
                <div className="flex-1 pr-6">
                    <h5 className="text-[10px] font-black text-gray-400 uppercase tracking-widest mb-3">GRAPHPATH</h5>
                    <p className="text-sm font-black text-gray-800 uppercase leading-snug">{candidate.target_job || candidate.sector || '분석 진행중'}</p>
                </div>
                <div className="flex-[1.5] px-6 border-l border-gray-100">
                    <h5 className="text-[10px] font-black text-gray-400 uppercase tracking-widest mb-3">MATCHEDGE</h5>
                    <p className="text-sm font-black text-gray-800 leading-snug">{matchStr}</p>
                </div>
                <div className="flex-1 pl-6 border-l border-gray-100 text-right flex flex-col justify-start">
                    <h5 className="text-[10px] font-black text-gray-400 uppercase tracking-widest mb-3">NODESCORE</h5>
                    <div className="flex justify-end items-end gap-3 text-right">
                        {candidate.graph_score !== undefined && <div className="text-[28px] leading-none font-black text-indigo-500">G: {candidate.graph_score.toFixed(2)}</div>}
                        {candidate.vector_score !== undefined && <div className="text-[28px] leading-none font-black text-blue-500 ml-1">V: {candidate.vector_score.toFixed(2)}</div>}
                    </div>
                </div>
            </div>
            
            <div className="flex items-center gap-6 text-xs font-bold text-gray-400 mb-12">
                <span className="flex items-center gap-1.5"><Phone className="w-3.5 h-3.5" /> {candidate.phone || candidate['전화번호'] || 'N/A'}</span>
                <span className="flex items-center gap-1.5"><Mail className="w-3.5 h-3.5" /> {candidate.email || candidate['이메일'] || 'N/A'}</span>
            </div>
        
            <div className="mb-6 flex items-center gap-2 text-black">
                <div className="w-6 h-6 bg-black rounded-full flex items-center justify-center"><Zap className="w-3 h-3 text-white fill-current" /></div>
                <h4 className="text-lg font-black uppercase tracking-tighter">Evidence Summary</h4>
            </div>
            
            <div className="bg-white border border-gray-200 shadow-sm rounded-[2.5rem] p-8 md:p-10 mb-4">
                <div className="mb-10 flex flex-col md:flex-row gap-6">
                    <div className="w-32 font-black text-black text-[13px] tracking-tight flex-shrink-0 pt-0.5">① 프로필 핵심 요약</div>
                    <div className="flex-1 text-[13px] font-bold text-gray-500 leading-relaxed whitespace-pre-wrap pt-[1px]">
                        "{summary}"
                    </div>
                </div>
                
                <div className="mb-10 flex flex-col md:flex-row gap-6">
                    <div className="w-32 font-black text-black text-[13px] tracking-tight flex-shrink-0 pt-0.5">② 경력 상세 이력</div>
                    <div className="flex-1">
                        {(!candidate.isParsed || !candidate.career) ? (
                            <div className="text-[13px] font-bold text-gray-400 pt-[1px]">파이프라인 분석 중...</div>
                        ) : (
                            <div className="space-y-4 mt-[1px]">
                                {candidate.career.map((chunk, idx) => (
                                    <div key={idx} className="flex justify-between items-start gap-4">
                                        <div className="flex-1 text-[13px] font-bold text-gray-500">
                                            {chunk.company_name}{chunk.department ? ,  : ''}{chunk.title ? ,  : ''}
                                        </div>
                                        <div className="text-[11px] font-bold text-gray-400 text-right whitespace-nowrap pt-0.5 uppercase tracking-widest">
                                            {chunk.duration}
                                        </div>
                                    </div>
                                ))}
                            </div>
                        )}
                    </div>
                </div>

                <div className="flex flex-col md:flex-row gap-6">
                    <div className="w-32 font-black text-black text-[13px] tracking-tight flex-shrink-0 pt-0.5">③ 학력 및 전공</div>
                    <div className="flex-1 text-[13px] font-bold text-gray-500 leading-relaxed whitespace-pre-wrap pt-[1px]">
                        {candidate.education || candidate['학력'] || '데이터 없음'}
                    </div>
                </div>
            </div>
        </div>
    );
  };

  const renderCandidateCard = (candidate, isModalExpanded = false) => {
    const isBookmarked = userBookmarks.includes(candidate.id);
    const name = (candidate.이름 || candidate.name || 'Unknown').replace(/\[.*?\]/, '').trim();
    const currentCompany = candidate.current_company || candidate.current || '미상';
    const sector = candidate.sector || '미분류';
    const titleSeniority = candidate.연차등급 || candidate.seniority || '미상';
    const summary = candidate.profile_summary || candidate['Experience Summary'] || candidate.snippet || '정보 없음';

    return (
      <div key={candidate.id} onClick={!isModalExpanded ? () => toggleExpand(candidate.id) : undefined} className={g-white rounded-[3rem] border  p-6 transition-all flex flex-col mb-4 relative cursor-pointer}>
        <div className="flex items-center gap-6 w-full">
            {isModalExpanded && (
              <button onClick={(e) => { e.stopPropagation(); setExpandedBookmarkId(null); }} className="absolute -top-3 -right-3 w-8 h-8 bg-black text-white rounded-full flex items-center justify-center shadow-md hover:bg-gray-800 transition-colors z-10">
                <ChevronUp className="w-4 h-4" />
              </button>
            )}
            <div className="w-14 h-14 bg-gray-50/80 rounded-full flex items-center justify-center flex-shrink-0 ml-2"><User className="w-6 h-6 text-gray-300" /></div>
            <div className="w-[15rem] flex-shrink-0 flex flex-col justify-center gap-1.5 ml-2">
              <div className="flex items-center gap-2 mb-1">
                <h3 className="text-[19px] font-black tracking-tight text-gray-900">{name}</h3>
                <span className="text-[10px] font-bold text-gray-400 uppercase italic">({titleSeniority})</span>
              </div>
              <div className="flex items-center text-[9px] font-black text-gray-400 uppercase tracking-widest leading-none">
                <span className="w-[105px]">CURRENT / LATEST :</span><span className="text-gray-600 truncate text-[10px]">{currentCompany}</span>
              </div>
              <div className="flex items-center text-[9px] font-black text-gray-400 uppercase tracking-widest leading-none mt-1">
                <span className="w-[105px]">MAIN SECTOR :</span><span className="text-gray-600 truncate text-[10px]">{sector}</span>
              </div>
            </div>
            <div className="flex-1 px-4"><p className="text-[13px] font-bold italic text-gray-400 leading-relaxed line-clamp-2 pr-6">"{summary}"</p></div>
            
            <div className="flex items-center gap-5 flex-shrink-0 mr-2">
              <div className="text-right hidden lg:block">
                {candidate.graph_score !== undefined && <div className="text-[11px] font-black tracking-widest text-[#111]">G: <span className="text-indigo-500">{candidate.graph_score.toFixed(2)}</span></div>}
                {candidate.vector_score !== undefined && <div className="text-[11px] font-black tracking-widest text-[#111] mt-[3px]">V: <span className="text-blue-500">{candidate.vector_score.toFixed(2)}</span></div>}
              </div>
              <button onClick={(e) => toggleBookmark(candidate.id, e)} className={w-10 h-10 rounded-full flex items-center justify-center transition-colors border }>
                <Bookmark className={w-4 h-4 } />
              </button>
              {!isModalExpanded && (
                <button className={w-10 h-10  rounded-full flex items-center justify-center transition-colors}>
                  {expandedBookmarkId === candidate.id ? <ChevronUp className="w-5 h-5" /> : <ChevronDown className="w-5 h-5" />}
                </button>
              )}
            </div>
        </div>

        {expandedBookmarkId === candidate.id && !isModalExpanded && (
          <div className="w-full mt-6 pt-6 border-t border-gray-100 cursor-default" onClick={e => e.stopPropagation()}>
            {renderCareerDetails(candidate, summary)}
          </div>
        )}
      </div>
    );
  };
'''
    
    with open('c:/Users/cazam/Downloads/이력서자동분석검색시스템/frontend_v2/src/App.jsx', 'w', encoding='utf-8') as f:
        f.write(before + replacement + '\n' + after)
    print('SUCCESS')
else:
    print('FAILED')

