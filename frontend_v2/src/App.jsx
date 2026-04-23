import React, { useState, useEffect } from 'react';
import { Search, User, Bookmark, Zap, X, Clock, ChevronDown, ChevronUp, LogOut, SlidersHorizontal, ArrowRight, Save, Info, Settings, Users, Database, ShieldAlert, Activity, Layers, Trash2, RotateCcw, Phone, Mail } from 'lucide-react';

export default function AntigravityMain() {
  const [token, setToken] = useState(localStorage.getItem('token') || '');
  const [currentUserData, setCurrentUserData] = useState(null);
  
  const [settings, setSettings] = useState({ wv: 0.6, wg: 0.4, synergy: 1.4, depth: 1.3 });
  const [userBookmarks, setUserBookmarks] = useState([]);
  const [userHistory, setUserHistory] = useState([]);
  const [historyPage, setHistoryPage] = useState(1);
  const [bookmarkPage, setBookmarkPage] = useState(1);
  const [searchPage, setSearchPage] = useState(1);
  const [bookmarkedCandidates, setBookmarkedCandidates] = useState([]);
  
  const [searchQuery, setSearchQuery] = useState("");
  const [quickFindQuery, setQuickFindQuery] = useState("");
  const [requiredKeywords, setRequiredKeywords] = useState("");
  
  // Seniority state changed to support multiple selections
  const SENIORITY_OPTIONS = ["무관", "JUNIOR", "MIDDLE", "SENIOR"];
  const [seniority, setSeniority] = useState(["무관"]);
  
  const [hasSearched, setHasSearched] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [isKeywordSearch, setIsKeywordSearch] = useState(false);
  
  const [candidates, setCandidates] = useState([]);
  const [totalCandidatesCount, setTotalCandidatesCount] = useState(0);

  const [isModalOpen, setIsModalOpen] = useState(!localStorage.getItem('token'));
  const [modalView, setModalView] = useState(!localStorage.getItem('token') ? 'login' : 'dashboard'); 

  const [loginInput, setLoginInput] = useState('');
  const [loginPassword, setLoginPassword] = useState('');
  const [loginError, setLoginError] = useState('');
  
  const [dashTab, setDashTab] = useState('history');
  const [sidebarSavedMsg, setSidebarSavedMsg] = useState('');
  const [expandedBookmarkId, setExpandedBookmarkId] = useState(null);
  const [isUserMenuOpen, setIsUserMenuOpen] = useState(false);

  // Admin states
  const [adminMetrics, setAdminMetrics] = useState({ total_candidates: 0, neo4j_edges: 0, pinecone_vectors: 0 });
  const [adminUsers, setAdminUsers] = useState([]);
  const [showAddUser, setShowAddUser] = useState(false);
  const [newUser, setNewUser] = useState({ id: '', name: '', password: '', role: 'user' });

  const headers = {
    'Content-Type': 'application/json',
    ...(token && { 'Authorization': `Bearer ${token}` })
  };

  useEffect(() => {
    if (token) {
      fetchUser();
      fetchBookmarks();
      fetchHistory();
    } else {
      setCurrentUserData(null);
      setIsModalOpen(true);
      setModalView('login');
    }
  }, [token]);

  useEffect(() => {
    if (isModalOpen && modalView === 'admin' && currentUserData?.is_admin) {
      fetchAdminData();
    }
  }, [isModalOpen, modalView, currentUserData]);

  const fetchUser = async () => {
    try {
      const res = await fetch('/api/auth/me', { headers });
      if (res.ok) {
        const data = await res.json();
        setCurrentUserData(data);
        setSettings(data.settings || { wv: 0.6, wg: 0.4, synergy: 1.4, depth: 1.3 });
        setIsModalOpen(false);
      } else {
        handleLogout();
      }
    } catch { handleLogout(); }
  };

  const fetchBookmarks = async () => {
    try {
      const res = await fetch('/api/bookmarks', { headers });
      if (res.ok) {
        const data = await res.json();
        setUserBookmarks(data.bookmarks);
      }
      const resCand = await fetch('/api/bookmarks/candidates', { headers });
      if (resCand.ok) {
        const dataCand = await resCand.json();
        setBookmarkedCandidates(dataCand.candidates);
      }
    } catch (e) { console.error(e); }
  };

  const fetchHistory = async () => {
    try {
      const res = await fetch('/api/history', { headers });
      if (res.ok) {
        const data = await res.json();
        setUserHistory(data.history);
      }
    } catch (e) { console.error(e); }
  };

  const fetchAdminData = async () => {
    try {
      const [mRes, uRes] = await Promise.all([
        fetch('/api/admin/metrics', { headers }),
        fetch('/api/admin/users', { headers })
      ]);
      if (mRes.ok) setAdminMetrics(await mRes.json());
      if (uRes.ok) setAdminUsers((await uRes.json()).users);
    } catch (e) { console.error(e); }
  };

  const handleLogin = async (e) => {
    e.preventDefault();
    try {
      const res = await fetch('/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ id: loginInput, password: loginPassword })
      });
      if (res.ok) {
        const data = await res.json();
        localStorage.setItem('token', data.token);
        setToken(data.token);
        setLoginError('');
        setLoginInput('');
        setLoginPassword('');
      } else {
        setLoginError('ID 또는 비밀번호를 확인해주세요.');
      }
    } catch (e) {
      setLoginError('서버 연결 실패');
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    setToken('');
    setCurrentUserData(null);
    setIsUserMenuOpen(false);
  };

  const handleWvChange = (e) => {
    const newWv = parseFloat(e.target.value);
    setSettings(prev => ({ ...prev, wv: newWv, wg: parseFloat((1 - newWv).toFixed(2)) }));
  };
  const handleSettingChange = (key, value) => {
    setSettings(prev => ({ ...prev, [key]: parseFloat(value) }));
  };

  const saveSettings = async () => {
    if (token) {
      const res = await fetch('/api/auth/settings', {
        method: 'PUT', headers, body: JSON.stringify(settings)
      });
      if (res.ok) {
        setSidebarSavedMsg('SAVED!');
        setTimeout(() => setSidebarSavedMsg(''), 2000);
      }
    }
  };
  
  const resetSettings = () => {
      setSettings({ wv: 0.6, wg: 0.4, synergy: 1.4, depth: 1.3 });
      if (token) {
        fetch('/api/auth/settings', {
          method: 'PUT', headers, body: JSON.stringify({ wv: 0.6, wg: 0.4, synergy: 1.4, depth: 1.3 })
        });
      }
  };

  const toggleBookmark = async (candidateId, e) => {
    if (e) e.stopPropagation();
    if (!token) return;
    try {
      const res = await fetch(`/api/bookmarks/${candidateId}`, { method: 'POST', headers });
      if (res.ok) {
        const data = await res.json();
        if (data.bookmarked) setUserBookmarks(prev => [...prev, candidateId]);
        else setUserBookmarks(prev => prev.filter(id => id !== candidateId));
      }
    } catch (e) { console.error(e); }
  };

  const toggleSeniority = (opt) => {
    if (opt === "무관") {
      setSeniority(["무관"]);
    } else {
      let newSel = seniority.filter(s => s !== "무관");
      if (newSel.includes(opt)) {
        newSel = newSel.filter(s => s !== opt);
        if (newSel.length === 0) newSel = ["무관"];
      } else {
        newSel.push(opt);
      }
      setSeniority(newSel);
    }
  };

  const executeQuickSearch = async (keyword) => {
    if (!keyword.trim() || !token) return;
    setHasSearched(true);
    setIsLoading(true);
    setIsKeywordSearch(true);
    setSearchPage(1);
    
    try {
      const res = await fetch(
        `/api/quick-search?q=${encodeURIComponent(keyword)}&limit=20`,
        { headers }
      );
      const data = await res.json();
      setCandidates(data.matched || []);
      setTotalCandidatesCount(data.total || 0);
      setSearchQuery(keyword);
    } catch(e) {
      setCandidates([]);
    } finally {
      setIsLoading(false);
    }
  };

  const executeSearch = async (queryParam) => {
    setIsKeywordSearch(false);
    const isEvent = queryParam && typeof queryParam === 'object';
    const finalQuery = (isEvent || !queryParam) ? searchQuery : queryParam;
    
    if (!finalQuery.trim() || !token) return;
    setHasSearched(true);
    setIsLoading(true);
    setSearchPage(1);
    
    fetch('/api/history', { method: 'POST', headers, body: JSON.stringify({ query: finalQuery }) }).then(fetchHistory);

    try {
      const reqKw = requiredKeywords.split(',').map(s=>s.trim()).filter(s=>s);
      
      const payload = {
        prompt: finalQuery, sectors: [], seniority: seniority,
        required: reqKw, preferred: [], weights: settings
      };

      const response = await fetch('/api/search-v8', { method: 'POST', headers, body: JSON.stringify(payload) });
      if (!response.ok) throw new Error('API Error');
      const data = await response.json();
      setCandidates(data.matched || []);
      setTotalCandidatesCount(data.total || (data.matched ? data.matched.length : 0));
    } catch (err) {
      setCandidates([]); setTotalCandidatesCount(0);
    } finally {
      setIsLoading(false);
    }
  };

  const handleHistoryClick = (query) => {
    setSearchQuery(query);
    setIsModalOpen(false);
    setTimeout(() => { executeSearch(); }, 100);
  };
  
  const goHome = () => {
    setHasSearched(false);
    setSearchQuery('');
    setCandidates([]);
    setIsKeywordSearch(false);
  };

  const toggleExpand = async (id) => {
    setExpandedBookmarkId(prev => prev === id ? null : id);
    const cand = candidates.find(c => c.id === id);
    if (cand && !cand.isParsed && cand.raw_career_text) {
      try {
        const response = await fetch('/api/parse-career', {
          method: 'POST', headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ candidate_id: id, raw_text: cand.raw_career_text })
        });
        const result = await response.json();
        setCandidates(prev => prev.map(c => c.id === id ? { ...c, career: result.career, isParsed: true } : c));
      } catch (err) { console.error(err); }
    }
  };

  const handleDeleteUser = async (userId) => {
      if(!window.confirm("정말 이 사용자를 시스템에서 강퇴하시겠습니까?")) return;
      try {
          const res = await fetch(`/api/admin/users/${userId}`, { method: 'DELETE', headers });
          if(res.ok) {
              fetchAdminData();
          } else {
              const err = await res.json();
              alert("강퇴 실패: " + err.detail);
          }
      } catch(err) { console.error(err); }
  };

  const handleAddUser = async (e) => {
      e.preventDefault();
      try {
          const res = await fetch('/api/admin/users', {
             method: 'POST', headers: headers,
             body: JSON.stringify(newUser)
          });
          if(res.ok) {
              setShowAddUser(false);
              setNewUser({ id: '', name: '', password: '', role: 'user' });
              fetchAdminData();
          } else {
              alert("계정 생성 실패");
          }
      } catch(err) { console.error(err); }
  }

  const renderCareerDetails = (candidate, passedSummary) => {
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
                    <div className="flex flex-col justify-end items-end gap-2 text-right">
                        {candidate.graph_score !== undefined && <div className="text-[28px] leading-none font-black text-indigo-500">G: {candidate.graph_score.toFixed(2)} <span className="text-[12px] font-black text-gray-300">/ 10.0</span></div>}
                        {candidate.vector_score !== undefined && <div className="text-[28px] leading-none font-black text-blue-500 ml-1">V: {candidate.vector_score.toFixed(2)} <span className="text-[12px] font-black text-gray-300">/ 1.00</span></div>}
                    </div>
                </div>
            </div>
            
            <div className="flex items-center gap-6 text-xs font-bold text-gray-400 mb-12">
                <span className="flex items-center gap-1.5"><Phone className="w-3.5 h-3.5" /> {candidate.phone || candidate['전화번호'] || 'N/A'}</span>
                <span className="flex items-center gap-1.5"><Mail className="w-3.5 h-3.5" /> {candidate.email || candidate['이메일'] || 'N/A'}</span>
                <span className="flex items-center gap-1.5"><User className="w-3.5 h-3.5" /> {(candidate.birth_year && String(candidate.birth_year).trim() !== '' && !String(candidate.birth_year).includes('미상') && !String(candidate.birth_year).includes('생년')) ? `${candidate.birth_year}년생` : '미상'}</span>
            </div>
        
            <div className="mb-6 flex items-center gap-2 text-black">
                <div className="w-6 h-6 bg-black rounded-full flex items-center justify-center"><Zap className="w-3 h-3 text-white fill-current" /></div>
                <h4 className="text-lg font-black uppercase tracking-tighter">Evidence Summary</h4>
            </div>
            
            <div className="bg-white border border-gray-200 shadow-sm rounded-[2.5rem] p-8 md:p-10 mb-4">
                <div className="mb-10 flex flex-col md:flex-row gap-6">
                    <div className="w-32 font-black text-black text-[13px] tracking-tight flex-shrink-0 pt-0.5">① 프로필 핵심 요약</div>
                    <div className="flex-1 text-[13px] font-bold text-gray-500 leading-relaxed whitespace-pre-wrap pt-[1px]">
                        "{passedSummary}"
                    </div>
                </div>
                
                <div className="mb-10 flex flex-col md:flex-row gap-6">
                    <div className="w-32 font-black text-black text-[13px] tracking-tight flex-shrink-0 pt-0.5">② 경력 상세 이력</div>
                    <div className="flex-1">
                        {(!candidate.careers && !candidate.career) ? (
                            <div className="text-[13px] font-bold text-gray-400 pt-[1px]">데이터가 없습니다.</div>
                        ) : (
                            <div className="space-y-4 mt-[1px]">
                                {(candidate.careers || candidate.career || []).map((chunk, idx) => (
                                    <div key={idx} className="flex justify-between items-start gap-4">
                                        <div className="flex-1 text-[13px] font-black text-gray-500">
                                            {chunk.company || chunk.company_name}{(chunk.team || chunk.department) ? `, ${chunk.team || chunk.department}` : ''}{(chunk.position || chunk.title) ? `, ${chunk.position || chunk.title}` : ''}
                                        </div>
                                        <div className="text-[12px] font-bold text-gray-400 whitespace-nowrap pt-0.5">
                                            {chunk.period || `${chunk.start_date || '?'} ~ ${chunk.end_date || '현재'}`}
                                        </div>
                                    </div>
                                ))}
                            </div>
                        )}
                    </div>
                </div>

                <div className="flex flex-col md:flex-row gap-6">
                    <div className="w-32 font-black text-black text-[13px] tracking-tight flex-shrink-0 pt-0.5">③ 학력</div>
                    <div className="flex-1 text-[13px] font-bold text-gray-500 leading-relaxed whitespace-pre-wrap pt-[1px]">
                        {Array.isArray(candidate.education) && candidate.education.length > 0 ? (
                            <div className="space-y-2">
                                {[...candidate.education].sort((a, b) => {
                                    const getLvl = (d) => {
                                        if(!d) return 4;
                                        if(d.includes('박사')) return 1;
                                        if(d.includes('석사')) return 2;
                                        if(d.includes('학사')) return 3;
                                        return 4;
                                    };
                                    return getLvl(a.degree) - getLvl(b.degree);
                                }).map((edu, idx) => {
                                    const periodStr = [edu.start_year || edu.start_date, edu.end_year || edu.end_date || edu.graduation_year].filter(x => x).join(' - ');
                                    return (
                                        <div key={idx}>
                                            {edu.school}{edu.major ? `, ${edu.major}` : ''}{edu.degree ? ` ${edu.degree}` : ''} {periodStr}
                                        </div>
                                    );
                                })}
                            </div>
                        ) : (
                            candidate.education || candidate['학력'] || '데이터 없음'
                        )}
                    </div>
                </div>
                
                {candidate.google_drive_url && (
                    <div className="flex justify-end mt-4 pt-4 border-t border-gray-100">
                        <a href={candidate.google_drive_url} target="_blank" rel="noopener noreferrer" className="inline-block px-5 py-2.5 bg-black text-white rounded-xl text-[10px] font-black tracking-widest hover:bg-gray-800 transition-colors uppercase shadow-sm" onClick={e => e.stopPropagation()}>
                            📄 OPEN CV
                        </a>
                    </div>
                )}
            </div>
        </div>
    );
  };

  const renderCandidateCard = (candidate, isModalExpanded = false) => {
    const isBookmarked = userBookmarks.map(String).includes(String(candidate.id));
    const name = (candidate.이름 || candidate.name || 'Unknown').replace(/\[.*?\]/, '').trim();
    const currentCompany = candidate.current_company || candidate.current || '미상';
    const sector = candidate.sector || '미분류';
    const titleSeniority = candidate.연차등급 || candidate.seniority || '미상';
    const summary = candidate.profile_summary || candidate["Experience Summary"] || candidate.snippet || '정보 없음';

    return (
      <div key={candidate.id} onClick={!isModalExpanded ? () => toggleExpand(candidate.id) : undefined} className={`bg-white rounded-[3rem] border ${expandedBookmarkId === candidate.id ? 'border-black shadow-lg rounded-[2.5rem]' : 'border-gray-100 shadow-sm hover:shadow-md hover:border-gray-300'} p-6 transition-all flex flex-col mb-4 relative cursor-pointer`}>
        <div className="flex items-center gap-6 w-full">
            {isModalExpanded && (
              <button onClick={(e) => { e.stopPropagation(); setExpandedBookmarkId(null); }} className="absolute -top-3 -right-3 w-8 h-8 bg-black text-white rounded-full flex items-center justify-center shadow-md hover:bg-gray-800 transition-colors z-10">
                <ChevronUp className="w-4 h-4" />
              </button>
            )}
            <div className="w-14 h-14 bg-gray-50/80 rounded-full flex items-center justify-center flex-shrink-0 ml-2"><User className="w-6 h-6 text-gray-300" /></div>
            <div className="w-[15rem] flex-shrink-0 flex flex-col justify-center gap-1.5 ml-2">
              <div className="flex items-center gap-2 mb-1">
                <h3 className="text-[19px] font-black tracking-tight text-gray-900 leading-none">{name}</h3>
                <span className="text-[10px] font-black text-[#d97706] uppercase italic">({titleSeniority})</span>
              </div>
              <div className="flex items-center text-[9px] font-black text-gray-400 uppercase tracking-widest leading-none mt-1">
                <span className="w-[105px]">CURRENT / LATEST :</span><span className="text-gray-900 font-black truncate text-[10px]">{currentCompany}</span>
              </div>
              <div className="flex items-center text-[9px] font-black text-gray-400 uppercase tracking-widest leading-none mt-1">
                <span className="w-[105px]">MAIN SECTOR :</span><span className="text-gray-900 font-black truncate text-[10px]">{sector}</span>
              </div>
            </div>
            <div className="flex-1 px-4"><p className="text-[13px] font-bold italic text-gray-400 leading-relaxed line-clamp-2 pr-6">"{summary}"</p></div>
            
            <div className="flex items-center gap-5 flex-shrink-0 mr-2">
              {candidate.is_keyword_match ? (
                <div className="text-[10px] font-black text-emerald-600 bg-emerald-50 px-2 py-1 rounded-lg border border-emerald-200">
                  KEYWORD
                </div>
              ) : (
                <div className="text-right hidden lg:block mr-2">
                  {candidate.graph_score !== undefined && <div className="text-[11px] font-black tracking-widest text-[#111]">G: <span className="text-indigo-500">{candidate.graph_score.toFixed(2)}</span></div>}
                  {candidate.vector_score !== undefined && <div className="text-[11px] font-black tracking-widest text-[#111] mt-[3px]">V: <span className="text-blue-500">{candidate.vector_score.toFixed(2)}</span></div>}
                  <div className="text-[9px] font-bold text-gray-500 tracking-widest mt-1.5 flex justify-end gap-2">
                    <span>⬡ {candidate.matched_edges ? candidate.matched_edges.length : 0} nodes</span>
                  </div>
                </div>
              )}
              <button onClick={(e) => toggleBookmark(String(candidate.id), e)} className={`w-10 h-10 rounded-full flex items-center justify-center transition-colors border ${isBookmarked ? 'bg-black border-black text-white hover:bg-gray-800' : 'bg-transparent border-gray-200 text-gray-400 hover:border-gray-400 hover:text-black hover:bg-gray-50'}`}>
                <Bookmark className={`w-4 h-4 ${isBookmarked ? 'fill-current' : ''}`} />
              </button>
              {!isModalExpanded && (
                <button className={`w-10 h-10 ${expandedBookmarkId === candidate.id ? 'bg-black text-white' : 'bg-transparent text-gray-300 hover:bg-gray-100 hover:text-gray-600'} rounded-full flex items-center justify-center transition-colors`}>
                  {expandedBookmarkId === candidate.id ? <ChevronUp className="w-5 h-5" /> : <ChevronDown className="w-5 h-5" />}
                </button>
              )}
            </div>
        </div>

        {/* Expanded UI explicitly extending the bounding box */}
        {expandedBookmarkId === candidate.id && !isModalExpanded && (
          <div className="w-full mt-6 pt-6 border-t border-gray-100 cursor-default" onClick={e => e.stopPropagation()}>
            {renderCareerDetails(candidate, summary)}
          </div>
        )}
      </div>
    );
  };

  const renderModals = () => {
    if (!isModalOpen) return null;

    if (!token) {
      return (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm animate-fade-in">
          <div className="bg-white w-full max-w-sm rounded-[2.5rem] shadow-2xl overflow-hidden p-10 relative">
            <div className="text-center mb-8">
              <div className="w-12 h-12 bg-black rounded-xl mx-auto mb-4 flex items-center justify-center"><User className="w-6 h-6 text-white" /></div>
              <h2 className="text-2xl font-black italic tracking-tighter uppercase mb-1">Login</h2>
              <p className="text-[10px] text-gray-400 font-bold tracking-widest uppercase">System Access</p>
            </div>
            <form onSubmit={handleLogin} className="space-y-4">
              <input type="text" placeholder="ID" value={loginInput} onChange={(e) => setLoginInput(e.target.value)} className="w-full bg-gray-50 border border-gray-200 rounded-xl px-4 py-3 text-sm font-bold focus:border-black outline-none" required />
              <input type="password" placeholder="Password" value={loginPassword} onChange={(e) => setLoginPassword(e.target.value)} className="w-full bg-gray-50 border border-gray-200 rounded-xl px-4 py-3 text-sm font-bold focus:border-black outline-none" required />
              {loginError && <p className="text-[10px] font-bold text-red-500">{loginError}</p>}
              <button type="submit" className="w-full bg-black text-white rounded-xl py-3.5 text-xs font-black tracking-widest uppercase hover:bg-gray-800 transition-colors mt-2">Sign In</button>
            </form>
          </div>
        </div>
      );
    }

    if (modalView === 'admin' && currentUserData?.is_admin) {
      return (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm animate-fade-in" onClick={() => setIsModalOpen(false)}>
          <div className="bg-[#f7f8fa] w-full max-w-7xl rounded-[2.5rem] shadow-2xl flex flex-col relative border border-gray-200/50 h-[90vh] overflow-hidden" onClick={(e) => e.stopPropagation()}>
            <div className="h-16 flex items-center justify-between px-8 border-b border-gray-200 bg-white flex-shrink-0">
                <div className="flex items-center gap-3"><Database className="w-4 h-4 text-black" /><span className="font-black text-sm uppercase tracking-widest text-black">Admin Console</span></div>
                <button onClick={() => setIsModalOpen(false)} className="flex items-center gap-1.5 px-3 py-2 bg-gray-100 hover:bg-gray-200 rounded-full text-gray-600 transition-colors"><X className="w-4 h-4" /><span className="text-[10px] font-black tracking-widest uppercase">Close</span></button>
            </div>
            <div className="flex-1 overflow-y-auto p-10 lg:px-16 custom-scrollbar relative">
              <div className="max-w-[1200px] mx-auto animate-fade-in pb-10">
                <div className="mb-10 flex justify-between items-end">
                  <div>
                    <h1 className="text-[3rem] font-black italic tracking-tighter uppercase text-black leading-none mb-2">ADMIN<br />CONSOLE.</h1>
                    <p className="text-sm font-bold text-gray-500">System Pipeline & User Management</p>
                  </div>
                </div>

                <div className="flex flex-col xl:flex-row gap-6 mb-6">
                  <div className="bg-white rounded-[2rem] border border-gray-100 shadow-sm p-8 xl:w-1/3 flex flex-col justify-between">
                    <div>
                      <div className="flex items-center gap-2 mb-8"><Database className="w-5 h-5 text-black" /><h2 className="text-sm font-black tracking-widest text-black uppercase">System Metrics</h2></div>
                      <div className="space-y-6">
                        <div><p className="text-[10px] font-black text-gray-400 uppercase tracking-widest mb-1">Total Candidates</p><p className="text-3xl font-black text-black">{adminMetrics.total_candidates.toLocaleString()} <span className="text-base font-bold text-gray-400 -ml-1">명</span></p></div>
                        <div><p className="text-[10px] font-black text-gray-400 uppercase tracking-widest mb-1">Neo4j Graph Edges</p><p className="text-3xl font-black text-black">{adminMetrics.neo4j_edges.toLocaleString()} <span className="text-base font-bold text-gray-400 -ml-1">개</span></p></div>
                        <div><p className="text-[10px] font-black text-gray-400 uppercase tracking-widest mb-1">Pinecone Vectors</p><p className="text-3xl font-black text-black">{adminMetrics.pinecone_vectors.toLocaleString()} <span className="text-base font-bold text-gray-400 -ml-1">개</span></p></div>
                      </div>
                    </div>
                  </div>

                  <div className="bg-white rounded-[2rem] border border-gray-100 shadow-sm p-8 xl:w-2/3">
                    <div className="flex justify-between items-center mb-8">
                      <div className="flex items-center gap-2"><Users className="w-5 h-5 text-black" /><h2 className="text-sm font-black tracking-widest text-black uppercase">User Access & Activity</h2></div>
                      <button onClick={()=>setShowAddUser(!showAddUser)} className="bg-gray-50 hover:bg-gray-100 text-black px-4 py-2 rounded-full text-[10px] font-black uppercase tracking-widest transition-colors flex items-center gap-1">
                         + Add User
                      </button>
                    </div>
                    
                    {showAddUser && (
                        <div className="mb-6 p-6 bg-gray-50 rounded-2xl border border-gray-200">
                            <form onSubmit={handleAddUser} className="flex gap-4">
                                <input type="text" placeholder="ID" value={newUser.id} onChange={(e)=>setNewUser({...newUser, id: e.target.value})} className="px-3 py-2 border rounded-lg text-sm w-32" required />
                                <input type="text" placeholder="Name" value={newUser.name} onChange={(e)=>setNewUser({...newUser, name: e.target.value})} className="px-3 py-2 border rounded-lg text-sm w-40" required />
                                <input type="password" placeholder="Password" value={newUser.password} onChange={(e)=>setNewUser({...newUser, password: e.target.value})} className="px-3 py-2 border rounded-lg text-sm w-40" required />
                                <button type="submit" className="px-4 py-2 bg-black text-white rounded-lg text-xs font-black uppercase">Create</button>
                            </form>
                        </div>
                    )}

                    <div className="overflow-x-auto">
                      <table className="w-full text-left border-collapse min-w-[600px]">
                        <thead>
                          <tr>
                            <th className="pb-4 text-[10px] font-black text-gray-400 uppercase tracking-widest">User</th>
                            <th className="pb-4 text-[10px] font-black text-gray-400 uppercase tracking-widest">Role</th>
                            <th className="pb-4 text-[10px] font-black text-gray-400 uppercase tracking-widest">Last Login</th>
                            <th className="pb-4 text-[10px] font-black text-gray-400 uppercase tracking-widest">Queries</th>
                            <th className="pb-4 text-[10px] font-black text-gray-400 uppercase tracking-widest text-right">Actions</th>
                          </tr>
                        </thead>
                        <tbody className="text-sm font-bold text-gray-700 divide-y divide-gray-50">
                          {adminUsers.map(u => (
                            <tr key={u.id} className="hover:bg-gray-50/50 transition-colors">
                                <td className="py-4">
                                <div className="flex items-center gap-2">
                                    <div className={`w-2 h-2 rounded-full ${u.is_admin ? 'bg-green-500' : 'bg-blue-400'}`}></div>
                                    <span className="text-black font-black">{u.name} {u.is_admin ? '(Admin)' : ''}</span>
                                </div>
                                </td>
                                <td className="py-4 text-gray-500">{u.role}</td>
                                <td className="py-4">{u.last_login || '-'}</td>
                                <td className="py-4">{u.queries || 0}회</td>
                                <td className="py-4 text-right">
                                    {!u.is_admin && (
                                        <button onClick={() => handleDeleteUser(u.id)} className="text-red-500 hover:text-red-700 p-1 rounded-md hover:bg-red-50 transition-colors">
                                           <Trash2 className="w-4 h-4" />
                                        </button>
                                    )}
                                </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      );
    }

    if (modalView === 'dashboard' && currentUserData) {
      return (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm animate-fade-in" onClick={() => setIsModalOpen(false)}>
          <div className="bg-[#f7f8fa] w-[95vw] max-w-[1700px] rounded-[2.5rem] shadow-2xl flex flex-col relative border border-gray-200/50 h-[92vh]" onClick={(e) => e.stopPropagation()}>
            <div className="h-16 flex items-center justify-between px-8 border-b border-gray-200 bg-white flex-shrink-0 rounded-t-[2.5rem]">
              <div className="flex items-center gap-3"><Settings className="w-4 h-4 text-black" /><span className="font-black text-sm uppercase tracking-widest text-black">Workspace</span></div>
              <button onClick={() => setIsModalOpen(false)} className="flex items-center gap-1.5 px-3 py-2 bg-gray-100 hover:bg-gray-200 rounded-full text-gray-600 transition-colors"><X className="w-4 h-4" /><span className="text-[10px] font-black tracking-widest uppercase">Close</span></button>
            </div>
            <div className="flex-1 flex overflow-hidden">
              <div className="w-80 flex-shrink-0 bg-white border-r border-gray-200 p-8 flex flex-col h-full overflow-y-auto custom-scrollbar">
                  <h3 className="text-xl font-black uppercase italic tracking-tighter text-black">{currentUserData?.name}</h3>
                  <p className="text-[10px] font-bold text-gray-400 tracking-widest uppercase mb-8">{currentUserData?.role}</p>
  
                  <div className="flex items-center justify-between mb-6">
                      <div className="flex items-center gap-2"><SlidersHorizontal className="w-4 h-4" /><h4 className="text-xs font-black uppercase tracking-widest text-black">Current Weights</h4></div>
                      <button onClick={resetSettings} className="w-7 h-7 rounded-full bg-gray-100 flex items-center justify-center hover:bg-black group transition-colors" title="Reset Weights">
                          <RotateCcw className="w-3.5 h-3.5 text-gray-600 group-hover:text-white transition-colors" />
                      </button>
                  </div>
                  
                  <div className="space-y-6">
                      <div className="flex justify-between items-center bg-gray-50 p-4 rounded-xl border border-gray-100">
                          <span className="text-[10px] font-black text-gray-500 uppercase tracking-wider">Vector</span>
                          <input type="number" step="0.1" value={settings.wv} onChange={handleWvChange} className="w-16 bg-transparent text-right font-black text-black outline-none border-b border-gray-300" />
                      </div>
                      <div className="flex justify-between items-center bg-gray-50 p-4 rounded-xl border border-gray-100">
                          <span className="text-[10px] font-black text-gray-500 uppercase tracking-wider">Graph</span>
                          <input type="number" step="0.1" value={settings.wg} disabled className="w-16 bg-transparent text-right font-black text-black outline-none border-b border-transparent" />
                      </div>
                      <div className="flex justify-between items-center bg-gray-50 p-4 rounded-xl border border-gray-100">
                          <span className="text-[10px] font-black text-gray-500 uppercase tracking-wider">Depth / Syn</span>
                          <div className="flex items-center gap-2">
                               <input type="number" step="0.1" value={settings.depth} onChange={(e) => handleSettingChange('depth', e.target.value)} className="w-12 bg-transparent text-right font-black text-black outline-none border-b border-gray-300" />
                               <span>/</span>
                               <input type="number" step="0.1" value={settings.synergy} onChange={(e) => handleSettingChange('synergy', e.target.value)} className="w-12 bg-transparent text-right font-black text-black outline-none border-b border-gray-300" />
                          </div>
                      </div>
                  </div>
  
                  <button onClick={saveSettings} className="w-full bg-black text-white hover:bg-gray-800 rounded-xl py-4 flex justify-center items-center gap-2 text-[10px] font-black uppercase tracking-widest mt-8 transition-colors">
                      <Save className="w-4 h-4" /> Save Settings {sidebarSavedMsg && `(${sidebarSavedMsg})`}
                  </button>
  
                  <div className="mt-8 p-6 bg-gray-50 rounded-2xl border border-gray-100 space-y-3">
                      <div className="flex items-center gap-2 mb-2"><Info className="w-4 h-4 text-black" /><span className="text-[10px] font-black uppercase tracking-widest text-black">Weights Guide</span></div>
                      <p className="text-[10px] font-bold text-gray-500 leading-relaxed">
                          <strong className="text-black uppercase tracking-wider">Vector:</strong> 문맥과 뉘앙스 유사성<br/><br/>
                          <strong className="text-black uppercase tracking-wider">Graph:</strong> 검증된 스킬/BUILT 매칭<br/><br/>
                          <strong className="text-black uppercase tracking-wider">Depth / Syn:</strong> 기술의 깊이/연관성 가산점
                      </p>
                  </div>
              </div>
              
              <div className="flex-1 p-10 bg-[#f7f8fa] flex flex-col items-center">
                  <div className="flex bg-white rounded-full p-2 border border-gray-200 shadow-sm w-max mb-8">
                      <button onClick={()=>setDashTab('history')} className={`px-8 py-2.5 rounded-full text-[10px] font-black uppercase tracking-widest transition-colors ${dashTab === 'history' ? 'bg-black text-white' : 'text-gray-400 hover:text-black'}`}>Search History</button>
                      <button onClick={()=>setDashTab('bookmarks')} className={`px-8 py-2.5 rounded-full text-[10px] font-black uppercase tracking-widest transition-colors flex items-center gap-2 ${dashTab === 'bookmarks' ? 'bg-black text-white' : 'text-gray-400 hover:text-black'}`}>Bookmarks <span className="bg-gray-100 text-black px-2 py-0.5 rounded-full">{userBookmarks.length}</span></button>
                  </div>
  
                  <div className="w-full max-w-[1200px] bg-white rounded-[2rem] border border-gray-100 shadow-sm p-8 flex-1 overflow-y-auto custom-scrollbar">
                      {dashTab === 'history' && (
                          <div className="space-y-2.5">
                              {userHistory.slice((historyPage - 1) * 10, historyPage * 10).map((h, i) => (
                                  <div key={i} onClick={() => handleHistoryClick(h.query)} className="group flex justify-between items-center px-5 py-2.5 rounded-2xl hover:bg-gray-50 border border-transparent hover:border-gray-200 transition-all cursor-pointer">
                                      <div className="flex items-center gap-4"><div className="w-8 h-8 rounded-full bg-gray-50 flex items-center justify-center group-hover:bg-white group-hover:shadow-sm"><Search className="w-3.5 h-3.5 text-gray-400" /></div><span className="text-sm font-black text-gray-800">{h.query}</span></div>
                                      <div className="flex items-center gap-2 text-[10px] font-bold text-gray-400 uppercase tracking-wider"><Clock className="w-3 h-3" />{h.created_at.substring(5,16).replace('T', ' ')}</div>
                                  </div>
                              ))}
                              {userHistory.length === 0 && <p className="text-center text-gray-400 text-sm mt-10">No search history found.</p>}
                              
                              {userHistory.length > 0 && (
                                <div className="flex justify-center gap-2 mt-6 pt-4 border-t border-gray-100">
                                  {Array.from({ length: Math.min(5, Math.ceil(userHistory.length / 10)) }, (_, i) => i + 1).map(p => (
                                    <button key={p} onClick={() => setHistoryPage(p)} className={`w-8 h-8 rounded-full flex items-center justify-center text-[10px] font-black transition-colors ${historyPage === p ? 'bg-black text-white' : 'bg-gray-100 text-gray-500 hover:bg-gray-200'}`}>
                                      {p}
                                    </button>
                                  ))}
                                </div>
                              )}
                          </div>
                      )}
                      {dashTab === 'bookmarks' && (
                          <div className="space-y-4">
                              {userBookmarks.length === 0 && <p className="text-center text-gray-400 text-sm mt-10">No bookmarks saved.</p>}
                              
                              {/* API 404 등 실패 시 이전에 쓰던 로직으로 폴백 (슬라이싱 포함) */}
                              {bookmarkedCandidates.length > 0 ? (
                                  bookmarkedCandidates.slice((bookmarkPage - 1) * 10, bookmarkPage * 10).map(cand => renderCandidateCard(cand))
                              ) : (
                                  candidates.filter(c => userBookmarks.map(String).includes(String(c.id))).slice((bookmarkPage - 1) * 10, bookmarkPage * 10).map(cand => renderCandidateCard(cand))
                              )}

                              {userBookmarks.length > 0 && bookmarkedCandidates.length === 0 && candidates.filter(c => userBookmarks.map(String).includes(String(c.id))).length === 0 && (
                                  <p className="text-center text-gray-400 text-sm mt-10 text-[10px] font-black tracking-widest uppercase">Backend needs restart / perform a search to see details.</p>
                              )}
                              
                              {userBookmarks.length > 0 && (
                                <div className="flex justify-center gap-2 mt-6 pt-4 border-t border-gray-100">
                                  {Array.from({ length: Math.ceil(userBookmarks.length / 10) }, (_, i) => i + 1).map(p => (
                                    <button key={p} onClick={() => setBookmarkPage(p)} className={`w-8 h-8 rounded-full flex items-center justify-center text-[10px] font-black transition-colors ${bookmarkPage === p ? 'bg-black text-white' : 'bg-gray-100 text-gray-500 hover:bg-gray-200'}`}>
                                      {p}
                                    </button>
                                  ))}
                                </div>
                              )}
                          </div>
                      )}
                  </div>
              </div>
            </div>
          </div>
        </div>
      );
    }
    
    return null;
  };

  return (
    <div className="flex h-screen bg-[#f7f8fa] text-gray-900 font-sans overflow-hidden">
      
      <aside className="w-[17rem] bg-white border-r border-gray-200 flex flex-col justify-between flex-shrink-0 z-10">
        <div className="flex-1 flex flex-col overflow-hidden">
          <div onClick={goHome} className="h-20 flex items-center px-6 gap-3 border-b border-gray-100 cursor-pointer hover:bg-gray-50 transition-colors flex-shrink-0 group">
            <div className="w-7 h-7 bg-black rounded flex flex-col items-center justify-center p-1.5 shadow-md shadow-black/20 group-hover:scale-105 transition-transform"><Layers className="w-full h-full text-white" strokeWidth={3} /></div>
            <span className="font-black text-xl tracking-tighter uppercase">Antigravity</span>
          </div>
          
          <div className="flex-1 overflow-y-auto px-6 pt-8 pb-4 custom-scrollbar">
            <div className="mb-6 flex items-center gap-2"><SlidersHorizontal className="w-5 h-5 text-black" /><h2 className="text-sm font-black uppercase tracking-widest text-black">Fusion Controls</h2></div>
            <p className="text-xs text-gray-800 font-black mb-8 leading-relaxed">{currentUserData ? `${currentUserData.name}님의 검색 가중치 설정입니다.` : ""}</p>

            <div className="space-y-10">
              <div>
                <label className="block text-[13px] font-black tracking-widest text-black uppercase mb-4">Vector vs Graph</label>
                <input type="range" min="0" max="1" step="0.05" value={settings.wv} onChange={handleWvChange} className="w-full h-1 bg-gray-300 rounded-full appearance-none cursor-pointer accent-black mb-3"/>
                <div className="flex justify-between">
                  <div className="flex flex-col"><span className="text-[10px] font-bold text-gray-500 uppercase">Vector</span><span className="text-sm font-black text-black">{settings.wv.toFixed(2)}</span></div>
                  <div className="flex flex-col text-right"><span className="text-[10px] font-bold text-gray-500 uppercase">Graph</span><span className="text-sm font-black text-black">{settings.wg.toFixed(2)}</span></div>
                </div>
              </div>
              <div>
                <div className="flex justify-between items-end mb-4"><label className="text-[13px] font-black tracking-widest text-black uppercase">Depth</label><span className="text-xs font-black text-black">x {settings.depth.toFixed(1)}</span></div>
                <input type="range" min="1.0" max="2.0" step="0.1" value={settings.depth} onChange={(e) => handleSettingChange('depth', e.target.value)} className="w-full h-1 bg-gray-300 rounded-full appearance-none cursor-pointer accent-black"/>
              </div>
              <div>
                <div className="flex justify-between items-end mb-4"><label className="text-[13px] font-black tracking-widest text-black uppercase">Synergy</label><span className="text-xs font-black text-black">x {settings.synergy.toFixed(1)}</span></div>
                <input type="range" min="1.0" max="2.0" step="0.1" value={settings.synergy} onChange={(e) => handleSettingChange('synergy', e.target.value)} className="w-full h-1 bg-gray-300 rounded-full appearance-none cursor-pointer accent-black"/>
              </div>
            </div>
            
            <div className="mt-8">
              <button disabled={isLoading} onClick={executeSearch} className="w-full bg-black hover:bg-gray-800 text-white py-3.5 rounded-xl text-[10px] font-black tracking-widest uppercase transition-colors flex items-center justify-center gap-2">Apply Pipeline <Zap className="w-3.5 h-3.5 fill-current" /></button>
            </div>
          </div>
        </div>
      </aside>

      <main className="flex-1 flex flex-col h-full overflow-hidden relative">
        <header className="h-20 bg-white border-b border-gray-200 flex items-center justify-between px-10 flex-shrink-0 z-10 shadow-sm relative">
          <div className="flex items-center gap-3 w-1/2 text-gray-400">
            <Search className="w-5 h-5 cursor-pointer hover:text-gray-600" onClick={() => { if(quickFindQuery.trim() !== '') executeQuickSearch(quickFindQuery); }} />
            <input 
              type="text" placeholder="Quick Find (Name, Phone, Email...)" 
              value={quickFindQuery} onChange={(e) => setQuickFindQuery(e.target.value)}
              onKeyDown={(e) => { if(e.key === 'Enter' && quickFindQuery.trim() !== '') executeQuickSearch(quickFindQuery); }}
              className="bg-transparent border-none outline-none w-full text-sm font-bold text-gray-800 placeholder-gray-400 focus:ring-0"
              disabled={!token}
            />
          </div>

          <div className="flex items-center gap-6">
            <div className="flex items-center gap-2 bg-gray-50 border border-gray-200 px-3 py-1.5 rounded-full"><div className="w-2 h-2 bg-black rounded-full animate-pulse"></div><span className="text-[9px] font-black tracking-widest text-gray-600">V8.6.0 REAL-TIME</span></div>
            
            <div className="relative">
              <button onClick={() => setIsUserMenuOpen(!isUserMenuOpen)} className={`w-10 h-10 border rounded-full flex items-center justify-center transition-all shadow-sm ${token ? 'bg-black border-black text-white' : 'bg-white border-gray-200 text-gray-600 hover:border-black hover:text-black'}`}><User className="w-4 h-4" /></button>
              
              {isUserMenuOpen && currentUserData && (
                <div className="absolute right-0 mt-2 w-56 bg-white border border-gray-200 rounded-2xl shadow-xl py-2 z-50 animate-fade-in">
                  <div className="px-4 py-3 border-b border-gray-100 mb-1">
                    <p className="text-sm font-black text-gray-900">{currentUserData.name}</p>
                    <p className="text-[10px] font-bold text-gray-400">{currentUserData.role}</p>
                  </div>
                  <button onClick={() => { setModalView('dashboard'); setIsModalOpen(true); setIsUserMenuOpen(false); }} className="w-full text-left px-4 py-2.5 text-xs font-bold text-gray-600 hover:bg-gray-50 hover:text-black flex items-center gap-2"><Settings className="w-4 h-4" /> Workspace Settings</button>
                  {currentUserData.is_admin && (
                    <button onClick={() => { setModalView('admin'); setIsModalOpen(true); setIsUserMenuOpen(false); }} className="w-full text-left px-4 py-2.5 text-xs font-bold text-gray-600 hover:bg-gray-50 hover:text-black flex items-center gap-2"><Database className="w-4 h-4" /> Admin Console</button>
                  )}
                  <button onClick={handleLogout} className="w-full text-left px-4 py-2.5 text-xs font-bold text-red-500 hover:bg-red-50 flex items-center gap-2 mt-1 border-t border-gray-100"><LogOut className="w-4 h-4" /> Log Out</button>
                </div>
              )}
            </div>
          </div>
        </header>

        <div className="flex-1 overflow-y-auto p-10 lg:px-16 xl:px-24 bg-[#f7f8fa] custom-scrollbar">
          {!hasSearched && (
            <div className="max-w-5xl mx-auto flex flex-col h-full min-h-[60vh] py-10 animate-fade-in-up">
              <div className="mb-12">
                <h2 className="text-6xl font-black italic tracking-tighter text-black uppercase leading-none mb-2 mt-4 inline-block">TARGETED<br/>TALENT SEARCH.</h2>
                <p className="text-xs font-bold text-gray-400 mt-2">데이터 정합성 기반 지능형 매칭 엔진</p>
              </div>
              
              <div className="bg-white border border-gray-200 rounded-[2rem] shadow-xl p-10 flex flex-col md:flex-row gap-10">
                <div className="w-full md:w-[45%] flex flex-col justify-between">
                  <div>
                    <div className="mb-10">
                      <label className="block text-md font-black uppercase tracking-widest text-[#111] mb-5">Seniority</label>
                      <div className="flex flex-wrap gap-2">
                        {SENIORITY_OPTIONS.map(opt => (
                            <button 
                              key={opt}
                              onClick={() => toggleSeniority(opt)}
                              className={`px-4 py-2 rounded-lg text-xs font-black uppercase tracking-widest transition-colors border shadow-sm ${seniority.includes(opt) ? 'bg-black text-white border-black' : 'bg-gray-50 text-gray-600 border-gray-200 hover:border-gray-400 hover:bg-white'}`}
                            >
                                {opt}
                            </button>
                        ))}
                      </div>
                    </div>
                    
                    <div className="mb-10">
                      <label className="block text-md font-black uppercase tracking-widest text-[#111] mb-5">Required Keywords</label>
                      <input 
                        type="text" 
                        placeholder="예: IPO, 자금조달, M&A" 
                        value={requiredKeywords} 
                        onChange={(e) => setRequiredKeywords(e.target.value)}
                        className="w-full bg-gray-50 border border-gray-200 rounded-xl px-5 py-4 text-sm font-bold text-gray-700 outline-none focus:border-black transition-colors"
                      />
                    </div>
                  </div>
                  
                  <button onClick={executeSearch} disabled={!token || isLoading} className="w-full bg-black text-white px-6 py-5 rounded-full text-[13px] font-black tracking-widest uppercase hover:bg-gray-800 transition-colors flex items-center justify-center gap-2">
                    Run Pipeline <Zap className="w-4 h-4 fill-current" />
                  </button>
                </div>
                
                <div className="w-full md:w-[55%] border-l border-gray-100 pl-10 flex flex-col">
                  <label className="block text-md font-black uppercase tracking-widest text-[#111] mb-5">Who are you looking for?</label>
                  <textarea 
                    placeholder="찾으시는 인재의 핵심 경험이나 배경을 입력해 주세요. (예: 상장(IPO)을 대비해서 자금 운용 및 주관사 대응을 주도해본 리드급 전문가)" 
                    value={searchQuery} 
                    onChange={(e) => setSearchQuery(e.target.value)}
                    onKeyDown={(e) => { if(e.key === 'Enter' && !e.shiftKey && searchQuery.trim() !== '') { e.preventDefault(); executeSearch(); } }}
                    className="flex-1 w-full bg-gray-50/50 border border-gray-200 rounded-[2rem] p-8 text-sm md:text-base font-bold text-gray-800 outline-none focus:border-black transition-colors resize-none placeholder-gray-400 leading-relaxed"
                    disabled={!token}
                  />
                </div>
              </div>
            </div>
          )}
          {hasSearched && (
            <div className="max-w-[1200px] mx-auto animate-fade-in-up">
              <div className="flex justify-between items-end mb-10 pb-6 border-b border-gray-200">
                <div>
                  <h2 className="text-[3rem] font-black italic tracking-tighter uppercase text-black leading-none mb-2">Talent<br />Intelligence.</h2>
                  {isKeywordSearch ? (
                    <p className="text-sm font-bold text-emerald-600">
                      '{searchQuery}' 키워드 검색 결과
                    </p>
                  ) : (
                    <p className="text-sm font-bold text-gray-500">
                      Gravity scoring system activated.
                    </p>
                  )}
                </div>
                <div className="text-right">
                  <p className="text-[10px] font-black tracking-widest text-gray-400 uppercase mb-1">Total Found</p>
                  <p className="text-4xl font-black text-black">{totalCandidatesCount}</p>
                </div>
              </div>
              {isLoading ? (
                <div className="py-32 flex flex-col items-center justify-center space-y-6">
                  <div className="w-12 h-12 border-4 border-gray-200 border-t-black rounded-full animate-spin"></div>
                  <p className="text-xs font-black tracking-widest text-gray-400 uppercase animate-pulse">Running Gravity Algorithm...</p>
                </div>
              ) : (
                <div>
                  {candidates.length > 0 ? (
                    <>
                      {candidates.slice((searchPage - 1) * 10, searchPage * 10).map(cand => renderCandidateCard(cand))}
                      {candidates.length > 10 && (
                        <div className="flex justify-center flex-wrap gap-2 mt-10 pt-6">
                          {Array.from({ length: Math.ceil(candidates.length / 10) }, (_, i) => i + 1).map(p => (
                            <button key={p} onClick={() => setSearchPage(p)} className={`w-8 h-8 rounded-full flex items-center justify-center text-[10px] font-black transition-colors ${searchPage === p ? 'bg-black text-white shadow-sm' : 'bg-transparent border border-gray-200 text-gray-500 hover:border-black hover:text-black'}`}>
                              {p}
                            </button>
                          ))}
                        </div>
                      )}
                    </>
                  ) : (
                    <p className="text-center py-20 text-gray-400 font-bold uppercase text-xs tracking-widest">No candidates found.</p>
                  )}
                </div>
              )}
            </div>
          )}
        </div>
      </main>

      <style dangerouslySetInnerHTML={{__html: `
        .animate-fade-in-up { animation: fadeInUp 0.6s cubic-bezier(0.16, 1, 0.3, 1) forwards; }
        .animate-fade-in { animation: fadeIn 0.3s ease-out forwards; }
        @keyframes fadeInUp { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }
        @keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
        .custom-scrollbar::-webkit-scrollbar { width: 8px; }
        .custom-scrollbar::-webkit-scrollbar-track { background: #f1f5f9; border-radius: 10px; margin: 4px; }
        .custom-scrollbar::-webkit-scrollbar-thumb { background-color: #cbd5e1; border-radius: 10px; border: 2px solid #f1f5f9; background-clip: padding-box; }
        .custom-scrollbar::-webkit-scrollbar-thumb:hover { background-color: #94a3b8; }
      `}} />

      {renderModals()}
    </div>
  );
}
