import React, { useState, useEffect } from 'react';
import { Search, User, Bookmark, Zap, X, Clock, ChevronDown, ChevronUp, LogOut, SlidersHorizontal, ArrowRight, Save, Info, Settings, Users, Database, ShieldAlert, Activity } from 'lucide-react';

// --- MOCK DATA FOR USERS ---
const MOCK_USERS = {
  liam: {
    id: 'liam',
    name: 'Liam (Admin)',
    role: 'System Administrator',
    password: 'password', // 테스트용
    isAdmin: true,
    status: 'ACTIVE',
    lastLogin: '방금 전',
    settings: { wv: 0.6, wg: 0.4, synergy: 1.4, depth: 1.3 },
    history: [],
    bookmarks: [] 
  },
  userB: {
    id: 'userB',
    name: 'Recruiter B',
    role: 'Tech Recruiter',
    password: 'password',
    isAdmin: false,
    status: 'ACTIVE',
    lastLogin: '2시간 전',
    settings: { wv: 0.8, wg: 0.2, synergy: 1.2, depth: 1.1 },
    history: [],
    bookmarks: []
  }
};

export default function AntigravityMain() {
  // Global State
  const [activeUserId, setActiveUserId] = useState(null);
  const [currentUserData, setCurrentUserData] = useState(null);
  const [settings, setSettings] = useState({ wv: 0.6, wg: 0.4, synergy: 1.4, depth: 1.3 });
  const [userBookmarks, setUserBookmarks] = useState([]);
  
  // Search State
  const [searchQuery, setSearchQuery] = useState("");
  const [requiredKeywords, setRequiredKeywords] = useState("");
  const [seniority, setSeniority] = useState('All');
  const [hasSearched, setHasSearched] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  
  // Data State
  const [candidates, setCandidates] = useState([]);
  const [totalCandidatesCount, setTotalCandidatesCount] = useState(0);

  // App View State ('main' | 'admin')
  const [appView, setAppView] = useState('main'); 

  // Modal State
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [modalView, setModalView] = useState('login'); 
  const [loginInput, setLoginInput] = useState('');
  const [loginError, setLoginError] = useState('');
  
  const [dashTab, setDashTab] = useState('history');
  const [sidebarSavedMsg, setSidebarSavedMsg] = useState('');
  const [expandedBookmarkId, setExpandedBookmarkId] = useState(null);
  
  const [historyPage, setHistoryPage] = useState(1);
  const [bookmarksPage, setBookmarksPage] = useState(1);
  const [isUserMenuOpen, setIsUserMenuOpen] = useState(false);

  // Sync state when user changes
  useEffect(() => {
    if (activeUserId && MOCK_USERS[activeUserId]) {
      const data = MOCK_USERS[activeUserId];
      setCurrentUserData(data);
      setSettings(data.settings);
      setUserBookmarks([...data.bookmarks]);
      setHistoryPage(1);
      setBookmarksPage(1);
      setExpandedBookmarkId(null);
      setModalView('dashboard');
    } else {
      setCurrentUserData(null);
      setModalView('login');
      setAppView('main');
    }
  }, [activeUserId]);

  const handleWvChange = (e) => {
    const newWv = parseFloat(e.target.value);
    setSettings(prev => ({ ...prev, wv: newWv, wg: parseFloat((1 - newWv).toFixed(2)) }));
  };

  const handleSettingChange = (key, value) => {
    setSettings(prev => ({ ...prev, [key]: parseFloat(value) }));
  };

  const saveSettings = () => {
    if (activeUserId) {
      MOCK_USERS[activeUserId].settings = { ...settings };
      setSidebarSavedMsg('SAVED!');
      setTimeout(() => setSidebarSavedMsg(''), 2000);
    }
  };

  const toggleBookmark = (candidateId, e) => {
    if (e) e.stopPropagation();
    if (!activeUserId) {
      alert("로그인 후 북마크 기능을 사용할 수 있습니다.");
      setIsModalOpen(true);
      return;
    }
    setUserBookmarks(prev => {
      const isBookmarked = prev.includes(candidateId);
      const newBookmarks = isBookmarked ? prev.filter(id => id !== candidateId) : [...prev, candidateId];
      MOCK_USERS[activeUserId].bookmarks = newBookmarks; 
      return newBookmarks;
    });
  };

  const handleLogin = (e) => {
    e.preventDefault();
    const user = MOCK_USERS[loginInput];
    if (user && user.password === 'password') {
      setActiveUserId(loginInput);
      setLoginError('');
      setLoginInput('');
      setIsModalOpen(false); // 로그인 성공 시 모달 닫기
    } else {
      setLoginError('ID를 확인해주세요. (liam 또는 userB)');
    }
  };

  const handleLogout = () => {
    setActiveUserId(null);
    setIsUserMenuOpen(false);
  };

  // --- API INTEGRATION ---
  const executeSearch = async () => {
    if (!searchQuery.trim()) return;
    setHasSearched(true);
    setIsLoading(true);
    
    // Add to History
    if (activeUserId && MOCK_USERS[activeUserId]) {
      const now = new Date();
      const timeStr = `${now.getMonth()+1}/${now.getDate()} ${now.getHours()}:${now.getMinutes()}`;
      MOCK_USERS[activeUserId].history.unshift({ query: searchQuery, time: timeStr });
    }

    try {
      const reqKw = requiredKeywords.split(',').map(s=>s.trim()).filter(s=>s);
      const payload = {
        prompt: searchQuery,
        sectors: [], // TODO: UI에서 섹터 멀티셀렉트 추가 시 반영
        seniority: seniority,
        required: reqKw,
        preferred: [],
        weights: settings // Fusion Controls을 백엔드로 넘김 (지원 시 활용)
      };

      const response = await fetch('/api/search-v8', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      
      if (!response.ok) throw new Error('API 응답 에러');
      const data = await response.json();
      
      setCandidates(data.matched || []);
      setTotalCandidatesCount(data.total || (data.matched ? data.matched.length : 0));
    } catch (err) {
      console.error(err);
      alert("검색 중 오류가 발생했습니다.");
      setCandidates([]);
      setTotalCandidatesCount(0);
    } finally {
      setIsLoading(false);
    }
  };

  const handleHistoryClick = (query) => {
    setSearchQuery(query);
    executeSearch();
    setIsModalOpen(false); 
  };
  
  const goHome = () => {
    setHasSearched(false);
    setSearchQuery('');
    setCandidates([]);
    setAppView('main');
  };

  const toggleExpand = async (id) => {
    setExpandedBookmarkId(prev => prev === id ? null : id);
    
    // 비동기 파싱 호출 (기존 Vanilla 로직 이식)
    const cand = candidates.find(c => c.id === id);
    if (cand && !cand.isParsed && cand.raw_career_text) {
      try {
        const response = await fetch('/api/parse-career', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ candidate_id: id, raw_text: cand.raw_career_text })
        });
        const result = await response.json();
        setCandidates(prev => prev.map(c => 
          c.id === id 
            ? { ...c, career: result.career, isParsed: true, isFallback: result.status === 'fallback' } 
            : c
        ));
      } catch (err) {
        console.error("Parsing Error", err);
      }
    }
  };


  // ==========================================
  // VIEW RENDERERS
  // ==========================================

  const renderWeightExplanations = () => (
    <div className="mt-6 p-4 bg-[#f8f9fa] rounded-2xl border border-gray-100 space-y-3">
      <div className="flex items-center gap-1.5 mb-1">
        <Info className="w-3.5 h-3.5 text-black" />
        <span className="text-[10px] font-black uppercase tracking-widest text-black">Weights Guide</span>
      </div>
      <p className="text-[10px] font-bold text-gray-500 leading-relaxed">
        <strong className="text-black uppercase tracking-wider">Vector:</strong> 문맥과 뉘앙스 유사성을 평가하여 숨은 인재를 찾습니다.<br/>
        <strong className="text-black uppercase tracking-wider mt-1.5 block">Graph:</strong> 검증된 스킬 매칭(BUILT 등)을 통해 정밀하게 타겟팅합니다.<br/>
        <strong className="text-black uppercase tracking-wider mt-1.5 block">Depth / Syn:</strong> 기술의 깊이(Depth)와 연관성(Synergy) 가산점입니다.
      </p>
    </div>
  );

  const renderCandidateCard = (candidate, isModalExpanded = false) => {
    const isBookmarked = userBookmarks.includes(candidate.id);
    
    // 실제 데이터 구조에 맞춘 필드 바인딩
    const name = (candidate.이름 || candidate.name || 'Unknown').replace(/\[.*?\]/, '').trim();
    const currentCompany = candidate.current_company || candidate.current || '미상';
    const sector = candidate.sector || '미분류';
    const titleSeniority = candidate.연차등급 || candidate.seniority || '미상';
    const summary = candidate.profile_summary || candidate["Experience Summary"] || candidate.snippet || '정보 없음';

    return (
      <div key={candidate.id} onClick={!isModalExpanded ? () => toggleExpand(candidate.id) : undefined} className={`bg-white rounded-[2rem] border ${expandedBookmarkId === candidate.id ? 'border-black shadow-lg' : 'border-gray-100 shadow-sm hover:shadow-md hover:border-gray-300'} p-5 pr-6 transition-all flex items-center gap-6 mb-4 relative cursor-pointer`}>
        {isModalExpanded && (
          <button 
            onClick={(e) => { e.stopPropagation(); setExpandedBookmarkId(null); }} 
            className="absolute -top-3 -right-3 w-8 h-8 bg-black text-white rounded-full flex items-center justify-center shadow-md hover:bg-gray-800 transition-colors z-10"
          >
            <ChevronUp className="w-4 h-4" />
          </button>
        )}
        <div className="w-14 h-14 bg-gray-50 border border-gray-100 rounded-2xl flex items-center justify-center flex-shrink-0">
          <User className="w-5 h-5 text-gray-300" />
        </div>
        <div className="w-48 flex-shrink-0 flex flex-col justify-center gap-1">
          <div className="flex items-center gap-2 mb-1">
            <h3 className="text-[17px] font-black tracking-tight text-gray-900">{name}</h3>
            <span className="text-[10px] font-bold text-gray-400 uppercase italic">({titleSeniority})</span>
          </div>
          <div className="flex items-center text-[10px] font-bold text-gray-500 uppercase tracking-tight">
            <span className="w-24 text-gray-400">CURRENT :</span>
            <span className="text-gray-800 truncate">{currentCompany}</span>
          </div>
          <div className="flex items-center text-[10px] font-bold text-gray-500 uppercase tracking-tight">
            <span className="w-24 text-gray-400">SECTOR :</span>
            <span className="text-gray-800 truncate">{sector}</span>
          </div>
        </div>
        <div className="flex-1 px-4">
          <p className="text-sm font-bold italic text-gray-400 leading-relaxed line-clamp-2 pr-4">"{summary}"</p>
        </div>
        
        <div className="flex items-center gap-3 flex-shrink-0">
          <div className="text-right mr-2 hidden lg:block">
            {candidate.graph_score !== undefined && (
               <div className="text-[10px] font-black text-indigo-500">G: {candidate.graph_score.toFixed(1)}</div>
            )}
            {candidate.vector_score !== undefined && (
               <div className="text-[10px] font-black text-blue-500">V: {candidate.vector_score.toFixed(2)}</div>
            )}
          </div>
          <button 
            onClick={(e) => toggleBookmark(candidate.id, e)}
            className={`w-10 h-10 rounded-full flex items-center justify-center transition-colors border ${isBookmarked ? 'bg-black border-black text-white hover:bg-gray-800' : 'bg-white border-gray-200 text-gray-400 hover:border-gray-400 hover:text-black'}`}
          >
            <Bookmark className={`w-4 h-4 ${isBookmarked ? 'fill-current' : ''}`} />
          </button>
          {!isModalExpanded && (
            <button className={`w-10 h-10 ${expandedBookmarkId === candidate.id ? 'bg-black text-white' : 'bg-gray-50 text-gray-400 hover:bg-gray-100'} border border-gray-100 rounded-full flex items-center justify-center transition-colors`}>
              {expandedBookmarkId === candidate.id ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
            </button>
          )}
        </div>

        {/* 세부 정보 확장 패널 (간단 버전) */}
        {expandedBookmarkId === candidate.id && !isModalExpanded && (
          <div className="absolute top-full left-0 w-full mt-2 bg-white border border-black shadow-xl rounded-2xl p-6 z-20 cursor-default" onClick={e => e.stopPropagation()}>
            <h4 className="text-xs font-black uppercase text-black mb-2">Detailed Profile Info</h4>
            <p className="text-sm text-gray-700 whitespace-pre-wrap">{summary}</p>
            {/* 향후 /api/parse-career 결과를 그려주는 UI 추가 부분 */}
          </div>
        )}
      </div>
    );
  };

  // --- ADMIN CONSOLE VIEW ---
  const renderAdminConsole = () => (
    <div className="flex-1 overflow-y-auto p-10 lg:px-16 xl:px-24 bg-[#f7f8fa] custom-scrollbar">
      {/* ... Admin View Code ... (Mockup 원본과 동일하게 유지) */}
      <div className="max-w-[1200px] mx-auto animate-fade-in">
        <div className="mb-10 flex justify-between items-end">
          <div>
            <h1 className="text-[3rem] font-black italic tracking-tighter uppercase text-black leading-none mb-2">ADMIN<br />CONSOLE.</h1>
            <p className="text-sm font-bold text-gray-500">System Pipeline & User Management</p>
          </div>
          <button onClick={() => setAppView('main')} className="flex items-center gap-2 text-[10px] font-black tracking-widest uppercase text-gray-400 hover:text-black transition-colors">
            <ArrowRight className="w-4 h-4 rotate-180" /> Back to Search
          </button>
        </div>
        {/* 생략: 메트릭 정보 등 UI 영역 */}
        <div className="bg-white rounded-3xl p-8 shadow-sm">
            <p className="text-gray-500 font-bold">관리자용 System Metrics 및 사용자 관리 기능이 이곳에 표시됩니다.</p>
        </div>
      </div>
    </div>
  );

  // --- MODALS ---
  const renderUserModal = () => {
    if (modalView === 'login') {
      return (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm animate-fade-in" onClick={() => setIsModalOpen(false)}>
          <div className="bg-white w-full max-w-sm rounded-[2.5rem] shadow-2xl overflow-hidden p-10 relative" onClick={e => e.stopPropagation()}>
            <button onClick={() => setIsModalOpen(false)} className="absolute top-6 right-6 text-gray-400 hover:text-black transition-colors"><X className="w-5 h-5" /></button>
            <div className="text-center mb-8">
              <div className="w-12 h-12 bg-black rounded-xl mx-auto mb-4 flex items-center justify-center">
                <User className="w-6 h-6 text-white" />
              </div>
              <h2 className="text-2xl font-black italic tracking-tighter uppercase mb-1">Login</h2>
              <p className="text-[10px] text-gray-400 font-bold tracking-widest uppercase">System Access</p>
            </div>
            <form onSubmit={handleLogin} className="space-y-4">
              <input type="text" placeholder="ID (liam or userB)" value={loginInput} onChange={(e) => setLoginInput(e.target.value)} className="w-full bg-gray-50 border border-gray-200 rounded-xl px-4 py-3 text-sm font-bold focus:border-black outline-none" />
              <input type="password" placeholder="Password" defaultValue="password" className="w-full bg-gray-50 border border-gray-200 rounded-xl px-4 py-3 text-sm font-bold focus:border-black outline-none" />
              {loginError && <p className="text-[10px] font-bold text-red-500">{loginError}</p>}
              <button type="submit" className="w-full bg-black text-white rounded-xl py-3.5 text-xs font-black tracking-widest uppercase hover:bg-gray-800 transition-colors mt-2">
                Sign In
              </button>
            </form>
          </div>
        </div>
      );
    }

    // Workspace View (Personalized)
    const maxHistoryCount = 50;
    const currentHistory = currentUserData?.history.slice(0, maxHistoryCount) || [];
    const maxHistoryPages = Math.ceil(currentHistory.length / 10);
    
    // 현재 북마크된 후보자를 Candidates에서 찾거나 Mock에서 가져옴
    const currentBookmarks = currentUserData ? candidates.filter(c => currentUserData.bookmarks.includes(c.id)) : [];
    const totalBookmarkPages = Math.ceil(currentBookmarks.length / 10);

    return (
      <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm animate-fade-in" onClick={() => setIsModalOpen(false)}>
        <div className="bg-[#f7f8fa] w-full max-w-5xl rounded-[2.5rem] shadow-2xl flex flex-col relative border border-gray-200/50 h-[85vh]" onClick={(e) => e.stopPropagation()}>
          <div className="h-16 flex items-center justify-between px-8 border-b border-gray-200 bg-white flex-shrink-0 rounded-t-[2.5rem]">
            {/* Header ... */}
            <div className="flex items-center gap-3"><Settings className="w-4 h-4 text-black" /><span className="font-black text-sm uppercase tracking-widest text-black">Workspace</span></div>
            <button onClick={() => setIsModalOpen(false)} className="flex items-center gap-1.5 px-3 py-2 bg-gray-100 hover:bg-gray-200 rounded-full text-gray-600 transition-colors"><X className="w-4 h-4" /><span className="text-[10px] font-black tracking-widest uppercase">Close</span></button>
          </div>
          <div className="flex-1 flex overflow-hidden">
            {/* ... Workspace Content (Mockup 동일 적용) ... */}
            <div className="w-72 bg-white border-r border-gray-200 p-8 flex flex-col h-full overflow-y-auto custom-scrollbar">
               {/* Controls */}
            </div>
            <div className="flex-1 p-8 bg-[#f7f8fa] flex flex-col h-full overflow-hidden">
                {/* History & Bookmarks */}
            </div>
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="flex h-screen bg-[#f7f8fa] text-gray-900 font-sans overflow-hidden">
      
      {/* 1. LEFT SIDEBAR */}
      <aside className="w-[17rem] bg-white border-r border-gray-200 flex flex-col justify-between flex-shrink-0 z-10">
        <div className="flex-1 flex flex-col overflow-hidden">
          <div onClick={goHome} className="h-20 flex items-center px-6 gap-3 border-b border-gray-100 cursor-pointer hover:bg-gray-50 transition-colors flex-shrink-0">
            <div className="w-7 h-7 bg-black rounded flex flex-col items-center justify-center gap-0.5 p-1.5 shadow-md shadow-black/20">
              <div className="w-full h-1 bg-white rounded-sm"></div>
              <div className="w-full h-1 bg-white rounded-sm"></div>
              <div className="w-full h-1 bg-white rounded-sm"></div>
            </div>
            <span className="font-black text-xl tracking-tighter uppercase">Antigravity</span>
          </div>
          
          <div className="flex-1 overflow-y-auto px-6 pt-8 pb-4 custom-scrollbar">
            <div className="mb-6 flex items-center gap-2">
              <SlidersHorizontal className="w-5 h-5 text-black" />
              <h2 className="text-sm font-black uppercase tracking-widest text-black">Fusion Controls</h2>
            </div>
            
            <p className="text-[10px] text-gray-500 font-bold mb-8 leading-relaxed">
              {currentUserData ? `${currentUserData.name}님의 실시간 검색 엔진 가중치 설정입니다.` : "비로그인 상태입니다. 설정 저장 시 로그인이 필요합니다."}
            </p>

            <div className="space-y-10">
              <div>
                <label className="block text-[12px] font-black tracking-widest text-black uppercase mb-4">Vector vs Graph</label>
                <input type="range" min="0" max="1" step="0.05" value={settings.wv} onChange={handleWvChange} className="w-full h-1 bg-gray-300 rounded-full appearance-none cursor-pointer accent-black mb-3"/>
                <div className="flex justify-between">
                  <div className="flex flex-col"><span className="text-[9px] font-bold text-gray-400 uppercase">Vector</span><span className="text-sm font-black text-black">{settings.wv.toFixed(2)}</span></div>
                  <div className="flex flex-col text-right"><span className="text-[9px] font-bold text-gray-400 uppercase">Graph</span><span className="text-sm font-black text-black">{settings.wg.toFixed(2)}</span></div>
                </div>
              </div>
              <div>
                <div className="flex justify-between items-end mb-4">
                  <label className="text-[12px] font-black tracking-widest text-black uppercase">Depth</label>
                  <span className="text-xs font-black text-black">x {settings.depth.toFixed(1)}</span>
                </div>
                <input type="range" min="1.0" max="2.0" step="0.1" value={settings.depth} onChange={(e) => handleSettingChange('depth', e.target.value)} className="w-full h-1 bg-gray-300 rounded-full appearance-none cursor-pointer accent-black"/>
              </div>
              <div>
                <div className="flex justify-between items-end mb-4">
                  <label className="text-[12px] font-black tracking-widest text-black uppercase">Synergy</label>
                  <span className="text-xs font-black text-black">x {settings.synergy.toFixed(1)}</span>
                </div>
                <input type="range" min="1.0" max="2.0" step="0.1" value={settings.synergy} onChange={(e) => handleSettingChange('synergy', e.target.value)} className="w-full h-1 bg-gray-300 rounded-full appearance-none cursor-pointer accent-black"/>
              </div>
            </div>
            
            {renderWeightExplanations()}

            <div className="mt-8">
              <button disabled={isLoading} onClick={executeSearch} className="w-full bg-black hover:bg-gray-800 text-white py-3.5 rounded-xl text-[10px] font-black tracking-widest uppercase transition-colors flex items-center justify-center gap-2">
                Apply Pipeline <Zap className="w-3.5 h-3.5 fill-current" />
              </button>
            </div>
          </div>
        </div>
      </aside>

      {/* 2. MAIN CONTENT AREA */}
      <main className="flex-1 flex flex-col h-full overflow-hidden relative">
        
        {/* TOP HEADER */}
        <header className="h-20 bg-white border-b border-gray-200 flex items-center justify-between px-10 flex-shrink-0 z-10 shadow-sm relative">
          <div className="flex items-center gap-3 w-1/2 text-gray-400">
            <Search className="w-5 h-5" />
            <input 
              type="text" placeholder="Quick Find (Name, Phone, Email...)" 
              value={searchQuery} onChange={(e) => setSearchQuery(e.target.value)}
              onKeyDown={(e) => { if(e.key === 'Enter' && searchQuery.trim() !== '') executeSearch(); }}
              className="bg-transparent border-none outline-none w-full text-sm font-bold text-gray-800 placeholder-gray-400 focus:ring-0"
            />
          </div>

          <div className="flex items-center gap-6">
            <div className="flex items-center gap-2 bg-gray-50 border border-gray-200 px-3 py-1.5 rounded-full">
              <div className="w-2 h-2 bg-black rounded-full animate-pulse"></div>
              <span className="text-[9px] font-black tracking-widest text-gray-600">V8.6.0 REAL-TIME</span>
            </div>
            
            <div className="relative">
              <button 
                onClick={() => {
                  if(!activeUserId) setIsModalOpen(true);
                  else setIsUserMenuOpen(!isUserMenuOpen);
                }}
                className={`w-10 h-10 border rounded-full flex items-center justify-center transition-all shadow-sm ${activeUserId ? 'bg-black border-black text-white' : 'bg-white border-gray-200 text-gray-600 hover:border-black hover:text-black'}`}
              >
                <User className="w-4 h-4" />
              </button>
              
              {/* User Dropdown Menu */}
              {isUserMenuOpen && activeUserId && (
                <div className="absolute right-0 mt-2 w-56 bg-white border border-gray-200 rounded-2xl shadow-xl py-2 z-50 animate-fade-in">
                  <div className="px-4 py-3 border-b border-gray-100 mb-1">
                    <p className="text-sm font-black text-gray-900">{currentUserData.name}</p>
                    <p className="text-[10px] font-bold text-gray-400">{currentUserData.role}</p>
                  </div>
                  <button 
                    onClick={() => { setIsModalOpen(true); setIsUserMenuOpen(false); }}
                    className="w-full text-left px-4 py-2.5 text-xs font-bold text-gray-600 hover:bg-gray-50 hover:text-black flex items-center gap-2"
                  >
                    <Settings className="w-4 h-4" /> Workspace Settings
                  </button>
                  {/* Admin Only Button */}
                  {currentUserData.isAdmin && (
                    <button 
                      onClick={() => { setAppView('admin'); setIsUserMenuOpen(false); }}
                      className="w-full text-left px-4 py-2.5 text-xs font-black text-blue-600 hover:bg-blue-50 flex items-center gap-2"
                    >
                      <ShieldAlert className="w-4 h-4" /> Admin Console
                    </button>
                  )}
                  <div className="border-t border-gray-100 mt-1 pt-1">
                    <button 
                      onClick={handleLogout}
                      className="w-full text-left px-4 py-2.5 text-xs font-bold text-red-500 hover:bg-red-50 flex items-center gap-2"
                    >
                      <LogOut className="w-4 h-4" /> Log Out
                    </button>
                  </div>
                </div>
              )}
            </div>
          </div>
        </header>

        {/* View Router (Main Search vs Admin Console) */}
        {appView === 'admin' ? renderAdminConsole() : (
          <div className="flex-1 overflow-y-auto p-10 lg:px-16 xl:px-24 bg-[#f7f8fa] custom-scrollbar">
            <div className="max-w-[1000px] mx-auto pb-20 animate-fade-in">
              {!hasSearched ? (
                <div className="pt-6">
                  {/* ... HOME VIEW ... */}
                  <div className="mb-10 animate-fade-in-up">
                    <h1 className="text-[4rem] font-black italic tracking-tighter uppercase text-black leading-[0.95] mb-3">TARGETED<br />TALENT SEARCH.</h1>
                    <p className="text-[13px] font-bold text-gray-400">데이터 정합성 기반 지능형 매칭 엔진</p>
                  </div>
                  <div className="bg-white rounded-[2.5rem] border border-gray-200 p-10 md:p-14 shadow-sm flex flex-col md:flex-row gap-12 lg:gap-16">
                    <div className="w-full md:w-[320px] flex flex-col flex-shrink-0">
                      <div className="mb-8">
                        <label className="block text-[11px] font-black tracking-widest text-black uppercase mb-4">SENIORITY</label>
                        <select onChange={(e) => setSeniority(e.target.value)} className="w-full bg-[#f8f9fa] border border-gray-200 rounded-2xl px-5 py-4 text-sm font-bold">
                            <option value="All">무관</option><option value="Junior">JUNIOR</option><option value="Middle">MIDDLE</option><option value="Senior">SENIOR</option>
                        </select>
                      </div>
                      <div className="mb-8">
                        <label className="block text-[11px] font-black tracking-widest text-black uppercase mb-4">REQUIRED KEYWORDS</label>
                        <input type="text" value={requiredKeywords} onChange={(e) => setRequiredKeywords(e.target.value)} placeholder="예: IPO, 자금조달" className="w-full bg-[#f8f9fa] border border-gray-200 rounded-2xl px-5 py-4 text-[13px] font-bold" />
                      </div>
                      <div className="mt-auto">
                        <button disabled={isLoading} onClick={executeSearch} className="w-full bg-black hover:bg-gray-800 text-white rounded-full px-8 py-4 text-[11px] font-black tracking-[0.2em] uppercase transition-colors">
                          {isLoading ? "LOADING..." : "RUN PIPELINE"}
                        </button>
                      </div>
                    </div>
                    <div className="flex-1 flex flex-col">
                      <label className="block text-[11px] font-black tracking-widest text-black uppercase mb-4">WHO ARE YOU LOOKING FOR?</label>
                      <textarea 
                        value={searchQuery} onChange={(e) => setSearchQuery(e.target.value)}
                        className="w-full flex-1 min-h-[300px] bg-white border border-gray-200 rounded-[2rem] p-8 text-sm font-bold outline-none focus:border-black resize-none"
                      />
                    </div>
                  </div>
                </div>
              ) : (
                <div className="pt-2">
                  {/* ... RESULTS VIEW ... */}
                  <div className="mb-10 flex justify-between items-end animate-fade-in-up">
                    <div>
                      <h2 className="text-2xl font-black italic tracking-tighter uppercase text-black mb-1">Search Results</h2>
                      <p className="text-xs font-bold text-gray-500">'{searchQuery}'에 대한 지능형 매칭 결과</p>
                    </div>
                    <div className="text-right">
                      <span className="text-[10px] font-black tracking-widest text-gray-400 uppercase">Matched Candidates</span>
                      <div className="text-xl font-black text-black">{totalCandidatesCount}</div>
                    </div>
                  </div>
                  
                  {isLoading ? (
                    <div className="flex justify-center p-20 animate-pulse text-gray-400 font-bold">API 실시간 분석 중...</div>
                  ) : candidates.length > 0 ? (
                    candidates.map(candidate => renderCandidateCard(candidate))
                  ) : (
                    <div className="flex justify-center p-20 text-gray-400 font-bold">해당 조건의 후보자가 없습니다.</div>
                  )}
                </div>
              )}
            </div>
          </div>
        )}
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
    </div>
  );
}
