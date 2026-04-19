
        const MAIN_SECTORS = ["AI", "DATA", "Finance", "HR", "HW", "MD", "PRODUCT", "STRATEGY", "SW", "디자인", "마케팅", "물류/유통", "반도체", "법무", "보안", "영업", "총무", "기타"];
        let state = { seniority: ['All'], selectedSectors: [], currentView: 'home', candidates: [] };

        function init() {
            renderSectors();
            lucide.createIcons();
            if (document.getElementById('opt-all')) {
                updateSeniorityUI();
            }
        }

        // Helper: Hash for client-side quick check
        const careerCache = new Map();
        function getHash(str) {
            let hash = 0;
            if(!str) return "0";
            for (let i = 0; i < str.length; i++) {
                hash = ((hash << 5) - hash) + str.charCodeAt(i);
                hash |= 0;
            }
            return hash.toString();
        }

        async function parseCareerWithAI(candidateId, rawText) {
            const hash = getHash(rawText);
            
            // 1. Client Cache check
            if (careerCache.has(hash)) {
                updateCandidateData(candidateId, careerCache.get(hash));
                return;
            }

            try {
                // Securely call local backend proxy
                const response = await fetch('/api/parse-career', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        candidate_id: candidateId,
                        raw_text: rawText
                    })
                });
                
                const result = await response.json();
                
                // 2. Write-back to Client Cache
                careerCache.set(hash, result.career);
                
                // 3. Update State & DB write-back is handled internally by backend
                updateCandidateData(candidateId, result.career, result.status === 'fallback');
                
            } catch (err) {
                console.error("Parsing API Error:", err);
                const fallbackData = [{company: "로딩 에러", team: "네트워크 불안정", position: "-", period: rawText}];
                updateCandidateData(candidateId, fallbackData, true);
            }
        }

        function updateCandidateData(id, careers, isFallback = false) {
            const idx = state.candidates.findIndex(c => c.id === id);
            if (idx !== -1) {
                state.candidates[idx].career = careers;
                state.candidates[idx].isParsed = true;
                state.candidates[idx].isFallback = isFallback;
                renderResults({ total: state.candidates.length, matched: state.candidates }, true);
            }
        }

        function renderSectors() {
            const list = document.getElementById('sidebar-sector-list');
            if (!list) return;
            list.innerHTML = MAIN_SECTORS.map(s => `<button onclick="toggleSector('${s}', this)" class="sector-btn text-left text-[12px] font-bold text-[#6B7280] py-2 px-3.5 hover:bg-slate-50 rounded-xl transition-all truncate flex items-center justify-between group">${s}<div class="indicator w-1.5 h-1.5 rounded-full bg-black opacity-0 transition-opacity"></div></button>`).join('');
        }

        function toggleSector(sector, el) {
            state.selectedSectors.includes(sector) ? state.selectedSectors = state.selectedSectors.filter(s => s !== sector) : state.selectedSectors.push(sector);
            el.classList.toggle('active');
        }

        function clearSectors() {
            state.selectedSectors = [];
            document.querySelectorAll('.sector-btn').forEach(btn => btn.classList.remove('active'));
        }

        function toggleSeniorityMenu() { document.getElementById('seniority-menu').classList.toggle('hidden'); }

        function toggleSeniority(val) {
            if (val === 'All') { state.seniority = ['All']; } 
            else {
                state.seniority = state.seniority.filter(s => s !== 'All');
                state.seniority.includes(val) ? state.seniority = state.seniority.filter(s => s !== val) : state.seniority.push(val);
                if (state.seniority.length === 0) state.seniority = ['All'];
            }
            updateSeniorityUI();
        }

        function updateSeniorityUI() {
            const textEl = document.getElementById('selected-seniority-text');
            if (!textEl) return;
            textEl.innerText = state.seniority.includes('All') ? '무관' : state.seniority.join(', ');
            ['All', 'Junior', 'Middle', 'Senior'].forEach(key => {
                const btn = document.getElementById(`opt-${key.toLowerCase()}`);
                if (!btn) return;
                const icon = btn.querySelector('i, svg');
                state.seniority.includes(key) ? (btn.classList.add('bg-slate-100', 'text-black'), icon && icon.classList.remove('opacity-0')) : (btn.classList.remove('bg-slate-100', 'text-black'), icon && icon.classList.add('opacity-0'));
            });
        }

        function resetAll() {
            state.seniority = ['All'];
            state.selectedSectors = [];
            document.getElementById('required-keywords').value = '';
            document.getElementById('search-prompt').value = '';
            document.getElementById('header-search').value = '';
            clearSectors();
            updateSeniorityUI();
        }

        function setView(view) {
            if (view === 'home') {
                resetAll();
            }
            state.currentView = view;
            document.getElementById('view-home').classList.toggle('hidden', view !== 'home');
            document.getElementById('view-results').classList.toggle('hidden', view !== 'results');
            lucide.createIcons();
        }

        async function startAnalyze() {
            const prompt = document.getElementById('search-prompt').value;
            const requiredKeywordsStr = document.getElementById('required-keywords').value;
            const reqKw = requiredKeywordsStr.split(',').map(s=>s.trim()).filter(s=>s);
            
            const payload = {
                prompt: prompt,
                sectors: state.selectedSectors,
                seniority: state.seniority.includes('All') ? 'All' : state.seniority[0],
                required: reqKw,
                preferred: []
            };

            setView('results');
            const container = document.getElementById('view-results');
            container.innerHTML = `<div class="py-40 flex flex-col items-center gap-6"><div class="w-10 h-10 border-4 border-slate-200 border-t-black rounded-full animate-spin"></div><p class="text-[10px] font-black tracking-[0.5em] text-slate-400 uppercase italic">Parsing Pipeline v8.6.0...</p></div>`;
            
            try {
                const response = await fetch('/api/search-v8', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });
                if(!response.ok) throw new Error('Network response was not ok');
                const data = await response.json();
                state.candidates = data.matched || [];
                renderResults({ total: data.total, matched: state.candidates });
            } catch (err) {
                container.innerHTML = `<div class="py-40 flex flex-col items-center gap-6"><p class="text-red-500 font-bold">오류가 발생했습니다: ${err.message}</p></div>`;
            }
        }

        function toggleExpand(id) {
            const cand = state.candidates.find(c => c.id === id);
            const el = document.getElementById(`detail-${id}`);
            const card = document.getElementById(`card-${id}`);
            if(!el || !card) return;

            const isHidden = el.classList.contains('hidden');
            document.querySelectorAll('[id^="detail-"]').forEach(d => d.classList.add('hidden'));
            document.querySelectorAll('.result-card').forEach(c => c.classList.remove('expanded'));
            
            if (isHidden) { 
                el.classList.remove('hidden'); 
                card.classList.add('expanded'); 
                
                // Trigger AI analysis if not already parsed
                if (!cand.isParsed) {
                    parseCareerWithAI(id, cand.raw_career_text);
                }
            }
        }

        function renderResults(data, preserveExpand = false) {
            const container = document.getElementById('view-results');
            const matched = data.matched || [];
            
            // Determine currently expanded ID to keep it open on fast updates
            let expandedId = null;
            if (preserveExpand) {
                const expandedEl = document.querySelector('.result-card.expanded');
                if (expandedEl) expandedId = expandedEl.id.replace('card-', '');
            }

            if (matched.length === 0) {
                container.innerHTML = `
                    <div class="flex items-end justify-between border-b border-[#E2E8F0] pb-6 mb-8">
                        <h2 class="text-2xl font-black uppercase text-black italic tracking-tighter">Candidate Matching Results</h2>
                        <button onclick="setView('home')" class="text-[10px] font-black text-indigo-600 uppercase tracking-widest hover:underline">New Query</button>
                    </div>
                    <div class="py-20 text-center"><p class="text-slate-500 font-bold">조건에 맞는 후보자가 없거나 검색어 분석에 실패했습니다.</p></div>
                `;
                return;
            }

            container.innerHTML = `
                <div class="flex items-end justify-between border-b border-[#E2E8F0] pb-6 mb-8">
                    <div class="space-y-1">
                        <h2 class="text-2xl font-black uppercase text-black italic tracking-tighter">Candidate Matching Results</h2>
                        <p class="text-[10px] text-[#9CA3AF] font-bold uppercase tracking-[0.2em]">Found ${data.total} relevant graph nodes</p>
                    </div>
                    <button onclick="setView('home')" class="text-[10px] font-black text-slate-500 uppercase tracking-widest hover:underline">New Query</button>
                </div>
                <div class="grid gap-5 pb-20">
                    ${matched.map((c, i) => {
                        const id = c.id || `cand-${i}`;
                        if (c.career && Array.isArray(c.career) && c.career.length > 0) { c.isParsed = true; }
                        let name = c.이름 || 'Unknown';
                        name = name.replace(/\[.*?\]/, '').trim();
                        const company = c.current_company || '미상';
                        const level = c.연차등급 || '확인 요망';
                        const sectorVal = c.sector || "미상";
                        
                        const matchedEdgesRaw = c.matched_edges || [];
                        const matchedEdges = matchedEdgesRaw.map(e => e.includes(':') ? e.split(':')[1] : e).filter(Boolean);
                        const highestEdge = matchedEdges.length > 0 ? matchedEdges[0] : "";
                        const companyRoleStr = [sectorVal, highestEdge].filter(Boolean).join(' > ');
                        
                        const summary = c.profile_summary || c["Experience Summary"] || '정보 없음';
                        const phone = c.연락처 || '번호 없음';
                        const email = c.email || '이메일 없음';
                        const notion_url = c.notion_url || '#';
                        const score = c._score || 0;
                        const missingEdges = c.missing_edges || [];
                        const birthYear = c.birth_year || '';
                        
                        const tags = c["Sub Sectors"] || [];
                        const pathWithTags = `${highestEdge ? sectorVal : '미분류'} ${tags.slice(0,3).map(s => `#${s.replace('#','')}`).join(' ')}`;
                        

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

                        const expandedCardCls = id === expandedId ? 'expanded' : '';

                        return `
                            <div id="card-${id}" class="result-card bg-white border border-[#E2E8F0] rounded-[32px] cursor-pointer overflow-hidden group shadow-sm ${expandedCardCls}" onclick="toggleExpand('${id}')">
                                <div class="p-8 flex items-center justify-between gap-8 h-[110px]">
                                    <div class="flex items-center gap-5 min-w-[260px] shrink-0">
                                        <div class="w-12 h-12 bg-slate-50 rounded-2xl flex items-center justify-center text-slate-300 group-hover:bg-black group-hover:text-white transition-all transform group-hover:rotate-6">
                                            <i data-lucide="user" class="w-6 h-6"></i>
                                        </div>
                                        <div class="space-y-0.5">
                                            <h3 class="text-xl font-black italic tracking-tighter">${name} <span class="text-[11px] font-bold uppercase ml-1 opacity-40">(${level})</span></h3>
                                            <p class="text-[12px] text-slate-500 font-bold tracking-tight"><span class="text-slate-400 mr-1.5 uppercase text-[9px]">Current / Latest :</span> ${company}</p>
                                            <p class="text-[12px] text-slate-500 font-bold tracking-tight mt-0.5"><span class="text-slate-400 mr-1.5 uppercase text-[9px]">Main Sector :</span> ${sectorVal}</p>
                                        </div>
                                    </div>
                                    <div class="flex-1 overflow-hidden">
                                        <p class="text-[13.5px] font-medium text-slate-400 leading-relaxed italic line-clamp-2 pr-4">"${summary}"</p>
                                    </div>
                                    <div class="w-10 h-10 rounded-full bg-slate-50 flex items-center justify-center text-slate-300 group-hover:text-black transition-colors shrink-0">
                                        <i data-lucide="chevron-down" class="w-5 h-5"></i>
                                    </div>
                                </div>

                                <div id="detail-${id}" class="${isExpandedHTML} border-t border-slate-50 bg-[#FBFCFD] p-12 animate-fade-in cursor-default" onclick="event.stopPropagation()">
                                    <div class="space-y-12">
                                        <div class="space-y-4 pb-10 border-b border-slate-100">
                                            <div class="grid grid-cols-10 gap-4 text-[11px] font-black uppercase tracking-tighter items-center">
                                                <div class="col-span-4 flex flex-col gap-1.5 pl-2">
                                                    <span class="text-slate-400 text-[9px]">Matched Nodes</span>
                                                    <span class="text-slate-800 leading-snug" style="font-size: 0.85rem; font-weight: 700; word-break: break-all; margin-bottom: 4px; display: block;">Top Skills: ${(c.top_skills || []).join(', ')}</span>
                                                    <span class="text-slate-800 leading-snug" style="font-size: 0.85rem; font-weight: 700; word-break: break-all; color: #4b5563;">Top Actions: ${(c.top_actions || []).join(', ')}</span>
                                                </div>
                                                <div class="col-span-3 flex flex-col gap-1.5 border-l border-slate-100 pl-6">
                                                    <span class="text-slate-400 text-[9px]">Graph Score</span>
                                                    <span class="text-indigo-600 text-[1.1rem] font-black">${c.graph_score || 0} <span class="text-xs text-slate-400">/ ${c.max_graph_score || 0}</span></span>
                                                </div>
                                                <div class="col-span-3 flex flex-col gap-1.5 border-l border-slate-100 pl-6">
                                                    <span class="text-slate-400 text-[9px]">Vector Score</span>
                                                    <span class="text-blue-600 text-[1.1rem] font-black">${c.vector_score || 0} <span class="text-xs text-slate-400">/ ${c.max_vector_score || 0}</span></span>
                                                </div>
                                            </div>
                                            <div class="flex items-center gap-10 text-[11px] font-bold text-slate-400 uppercase tracking-[0.1em] pt-4">
                                                <span class="flex items-center gap-2"><i data-lucide="phone" class="w-3.5 h-3.5 text-slate-300"></i> ${phone}</span>
                                                <span class="flex items-center gap-2"><i data-lucide="mail" class="w-3.5 h-3.5 text-slate-300"></i> ${email}</span>
                                                <span class="flex items-center gap-2"><i data-lucide="calendar" class="w-3.5 h-3.5 text-slate-300"></i> ${c.birth_year ? c.birth_year + '년생' : '생년 미상'}</span>
                                            </div>
                                        </div>

                                        <div class="space-y-6">
                                            <div class="flex items-center gap-3">
                                                <div class="w-6 h-6 bg-black rounded-full flex items-center justify-center">
                                                    <i data-lucide="zap" class="w-3.5 h-3.5 text-white"></i>
                                                </div>
                                                <p class="text-[15px] font-black text-black uppercase tracking-[0.1em]">Evidence Summary</p>
                                            </div>
                                            <div class="p-10 bg-white border border-slate-100 rounded-[40px] shadow-inner relative overflow-hidden group/box hover:border-black transition-all">
                                                <div class="space-y-10">
                                                    <div class="flex gap-5 items-start">
                                                        <span class="text-[14px] font-black text-slate-800 shrink-0 mt-0.5">① 프로필 핵심 요약</span>
                                                        <p class="text-[15px] font-medium text-slate-700 leading-relaxed">${c.profile_summary || '분석 중...'}</p>
                                                    </div>
                                                    
                                                    <div class="flex flex-col gap-4 pt-10 border-t border-slate-100">
                                                        <div class="flex gap-5 items-start">
                                                            <span class="text-[14px] font-black text-slate-800 shrink-0 mt-0.5">② 경력 상세 이력</span>
                                                            <div class="space-y-6 flex-1">
                                                                <div id="timeline-${id}" class="space-y-0 text-[14.5px] font-medium text-slate-700">
                                                                    ${c.isParsed && c.career ? 
                                                                        c.career.map(h => c.isFallback ? 
                                                                            `<p class="leading-relaxed whitespace-pre-line text-[13.5px] text-slate-500">${h.period}</p>`
                                                                        :
                                                                            `<div class="flex items-center justify-between group/line border-b border-slate-50 border-dotted py-3.5 last:border-0 hover:bg-slate-50 -mx-4 px-4 rounded-xl transition-all">
                                                                                <p class="text-[14px] font-bold text-slate-800">
                                                                                    ${h.company}, <span class="text-slate-500 font-medium">${h.team}</span>, <span class="text-slate-400">${h.position}</span>
                                                                                </p>
                                                                                <span class="text-[12px] font-black text-slate-300 group-hover/line:text-black transition-colors">${h.period}</span>
                                                                            </div>`
                                                                        ).join('') :
                                                                        `<div class="py-4 flex items-center gap-3 animate-pulse-subtle">
                                                                            <div class="w-4 h-4 border-2 border-slate-200 border-t-black rounded-full animate-spin"></div>
                                                                            <p class="text-[13px] font-bold text-slate-400 uppercase tracking-widest">Gemini AI가 비정형 데이터를 구조화하는 중입니다...</p>
                                                                        </div>`
                                                                    }
                                                                </div>
                                                            </div>
                                                        </div>
                                                        <div class="flex gap-5 items-start pt-10 mt-6 border-t border-slate-100">
                                                            <span class="text-[14px] font-black text-slate-800 shrink-0 mt-0.5">③ 학력</span>
                                                            <div class="space-y-4 flex-1 text-[13.5px] font-medium text-slate-700">
                                                                ${(c.education_json && c.education_json.length > 0) ? c.education_json.map(edu => 
                                                                    `<div class="flex items-center justify-between border-b border-slate-50 border-dotted py-2 last:border-0">
                                                                        <p><span class="font-bold text-black">${edu.schoolName || edu.school || '학교명 없음'}</span>, ${edu.major || ''} <span class="text-slate-400 ml-1">(${edu.degree})</span></p>
                                                                    </div>`
                                                                ).join('') : '<p class="text-slate-400 italic">등록된 학력 정보 없음</p>'}
                                                            </div>
                                                        </div>
                                                    </div>
                                                </div>
                                            </div>
                                        </div>

                                        ${missingEdges.length > 0 ? `
                                            <div class="space-y-6">
                                                <div class="flex items-center gap-3">
                                                    <i data-lucide="alert-circle" class="w-6 h-6 text-black"></i>
                                                    <p class="text-[15px] font-black text-black uppercase tracking-[0.1em]">Interview Focus (Verification)</p>
                                                </div>
                                                <div class="p-8 bg-slate-50 border border-slate-200 rounded-[32px]">
                                                    <ul class="space-y-3">
                                                        ${missingEdges.map(e => e.includes(':') ? e.split(':')[1] : e).filter(Boolean).map(m => `
                                                            <li class="flex items-center gap-3 text-[14px] font-bold text-slate-700">
                                                                <div class="w-1.5 h-1.5 rounded-full bg-black"></div>
                                                                ${m} 경험에 대한 사전 검증(Reference) 필요
                                                            </li>
                                                        `).join('')}
                                                    </ul>
                                                </div>
                                            </div>
                                        ` : ''}

                                        <div class="pt-10 border-t border-slate-100 flex justify-end">
                                            <a href="${c.google_drive_url || notion_url || '#'}" target="_blank" class="flex items-center gap-3 px-10 py-4.5 bg-black text-white rounded-full text-[11px] font-black uppercase tracking-widest hover:scale-105 transition-all shadow-xl shadow-black/10">
                                                Open CV 원문 <i data-lucide="external-link" class="w-4 h-4"></i>
                                            </a>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        `;
                    }).join('')}
                </div>
            `;
            lucide.createIcons();
        }

        window.onload = init;
    