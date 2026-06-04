import json, sqlite3, re, time
from datetime import datetime
import google.generativeai as genai
from ontology_graph import CANONICAL_MAP, SKILL_BIRTH_YEAR

# Gemini 초기화
secrets = json.load(open('secrets.json', encoding='utf-8'))
genai.configure(api_key=secrets['GEMINI_API_KEY'])
model = genai.GenerativeModel('gemini-2.0-flash')

# ── 스킬 희소성 계산 ──────────────────────────────
def get_skill_rarity(skill: str, year_used: int, node_idf: dict) -> float:
    """스킬 희소성 = DB 희소성 + 성숙도 보정 + 시점 보정"""
    db_rarity = node_idf.get(skill, 0.5)

    birth_year = SKILL_BIRTH_YEAR.get(skill, 2010)
    skill_age = 2025 - birth_year
    maturity_penalty = min(skill_age / 10, 1.0)

    years_after_birth = max(year_used - birth_year, 0)
    timing_score = max(0.0, 1.0 - years_after_birth / 5.0)

    rarity = (
        db_rarity * 0.5 +
        (1.0 - maturity_penalty) * 0.3 +
        timing_score * 0.2
    )
    return round(min(rarity, 1.0), 3)

def get_combo_rarity(skills: list, conn: sqlite3.Connection,
                     node_idf: dict) -> float:
    """스킬 조합 희소성 - 조합 보유자가 적을수록 높음"""
    if not skills:
        return 0.0
    if len(skills) == 1:
        return node_idf.get(skills[0], 0.5)

    cur = conn.cursor()
    # 스킬 조합 동시 보유자 수 (Neo4j 대신 profile_summary 기반 추정)
    conditions = ' AND '.join([
        f"(profile_summary LIKE '%{s.replace('_',' ')}%' OR profile_summary LIKE '%{s}%')"
        for s in skills[:3]
    ])
    try:
        cur.execute(
            f"SELECT COUNT(*) FROM candidates "
            f"WHERE is_duplicate=0 AND {conditions}")
        combo_count = cur.fetchone()[0]
    except:
        combo_count = 100

    total = 3500
    combo_rarity = 1.0 - min(combo_count / total, 1.0)
    individual_avg = sum(node_idf.get(s, 0.5) for s in skills) / len(skills)

    return round(0.4 * individual_avg + 0.6 * combo_rarity, 3)

# ── Company Signal (Gemini 웹서치) ────────────────
COMPANY_CACHE = {}  # 동일 회사 중복 호출 방지

def get_company_signal(company: str, position: str,
                       start_year: int, end_year: int) -> dict:
    """Gemini로 회사+포지션+시점 기반 신호 추론"""
    cache_key = f"{company}_{start_year}_{end_year}"
    if cache_key in COMPANY_CACHE:
        return COMPANY_CACHE[cache_key]

    if not company or company.strip() == '':
        return {"tier": "C", "timing_score": 0.5,
                "domain_relevance": 0.5, "company_summary": "unknown", "confidence": 0.3}

    prompt = f"""
회사명: {company}
포지션: {position}
재직기간: {start_year}년 ~ {end_year}년

위 정보를 바탕으로 아래 항목을 평가해줘.
JSON만 반환. 설명 없음.

{{
  "tier": "S/A/B/C",
  "timing_score": 0.0~1.0,
  "domain_relevance": 0.0~1.0,
  "company_summary": "20자 이내",
  "confidence": 0.0~1.0
}}

tier 기준:
  S: 글로벌 빅테크, 국내 탑티어 (Google/Meta/삼성전자/네이버/카카오)
  A: 유니콘/준유니콘, 업계 선도 스타트업 (토스/쿠팡/당근/리벨리온)
  B: 중견기업, 성장 스타트업
  C: 일반 중소기업

timing_score 기준:
  재직 시점이 그 회사/도메인의 전성기였는가
  1.0 = 폭발 성장기 한가운데
  0.5 = 평범한 시기
  0.2 = 침체기/몰락기

domain_relevance:
  해당 포지션이 그 회사의 핵심 도메인인가
  1.0 = 그 회사의 대표 직무
  0.5 = 관련 있음
  0.2 = 비핵심
"""
    try:
        resp = model.generate_content(prompt)
        text = resp.text.strip()
        # JSON 추출
        match = re.search(r'\{.*\}', text, re.DOTALL)
        if match:
            result = json.loads(match.group())
            COMPANY_CACHE[cache_key] = result
            return result
    except Exception as e:
        pass

    default = {"tier": "B", "timing_score": 0.5,
               "domain_relevance": 0.5,
               "company_summary": company,
               "confidence": 0.4}
    COMPANY_CACHE[cache_key] = default
    return default

# ── Tenure Signal ─────────────────────────────────
def get_tenure_signal(careers: list) -> dict:
    """재직 패턴 분석 - 계산으로 측정"""
    if not careers:
        return {"avg_tenure": 0, "trajectory": "unknown",
                "job_count": 0}

    tenures = []
    for c in careers:
        duration = c.get('duration_years') or c.get('duration', 0)
        if isinstance(duration, str):
            # "3년 2개월" 파싱
            years = re.findall(r'(\d+)\s*년', duration)
            months = re.findall(r'(\d+)\s*개월', duration)
            y = int(years[0]) if years else 0
            m = int(months[0]) if months else 0
            duration = y + m / 12
        tenures.append(float(duration) if duration else 1.0)

    avg_tenure = sum(tenures) / len(tenures) if tenures else 0

    # 이직 방향성
    if avg_tenure >= 3.0:
        trajectory = "stable"
    elif avg_tenure >= 1.5:
        trajectory = "normal"
    else:
        trajectory = "frequent"

    return {
        "avg_tenure": round(avg_tenure, 1),
        "trajectory": trajectory,
        "job_count": len(careers),
    }

# ── Evidence Signal ───────────────────────────────
def get_evidence_signal(raw_text: str) -> dict:
    """이력서 텍스트 패턴 분석"""
    if not raw_text:
        return {"has_numbers": False, "number_density": 0.0, "action_score": 0.0,
                "completeness": 0.0}

    # 숫자/수치 존재 여부
    number_patterns = re.findall(
        r'\d+[%억만원TPS개명]\w*|\d+\s*[%억만]', raw_text)
    has_numbers = len(number_patterns) > 0
    number_density = min(len(number_patterns) / 10, 1.0)

    # 직접 실행 동사
    action_verbs = ['설계', '구현', '개발', '구축', '런칭', '출시',
                    '리딩', '총괄', '주도', '달성', '개선', '최적화',
                    'designed', 'built', 'led', 'launched', 'achieved']
    passive_verbs = ['참여', '지원', '보조', '담당', 'participated']

    action_count = sum(1 for v in action_verbs if v in raw_text)
    passive_count = sum(1 for v in passive_verbs if v in raw_text)
    total = action_count + passive_count + 1
    action_score = round(action_count / total, 2)

    # 이력서 완성도
    completeness_signals = [
        len(raw_text) > 500,
        has_numbers,
        action_count > 3,
        bool(re.search(r'\d{4}', raw_text)),  # 날짜 있음
    ]
    completeness = sum(completeness_signals) / len(completeness_signals)

    return {
        "has_numbers": has_numbers,
        "number_density": round(number_density, 2),
        "action_score": action_score,
        "completeness": round(completeness, 2),
    }

# ── 최종 CEI 생성 ─────────────────────────────────
def generate_cei(candidate: dict, conn: sqlite3.Connection,
                 node_idf: dict) -> dict:
    """후보자 CEI 전체 생성"""

    cid = candidate['id']
    name = candidate.get('name_kr') or candidate.get('name', '')
    sector = candidate.get('sector', '')
    company = candidate.get('current_company', '')
    raw_text = candidate.get('raw_text', '') or ''
    careers_json = candidate.get('careers_json', '[]') or '[]'

    try:
        careers = json.loads(careers_json)
        if not isinstance(careers, list):
            careers = []
    except:
        careers = []

    # ── 1. Company Signal ──
    # 현재 회사 기준 (가장 최근 경력)
    main_company = careers[0] if careers else {}
    start_year = 2020  # fallback
    end_year = 2025

    comp_signal = get_company_signal(
        company or main_company.get('company', ''),
        main_company.get('role', '') or main_company.get('title', ''),
        start_year, end_year
    )

    tier_score = {'S': 1.0, 'A': 0.80, 'B': 0.55, 'C': 0.30}
    company_score = tier_score.get(comp_signal.get('tier', 'B'), 0.55)

    # ── 2. Tenure Signal ──
    tenure_sig = get_tenure_signal(careers)
    tenure_score = min(tenure_sig['avg_tenure'] / 5.0, 1.0)

    # ── 3. Tech Signal ──
    # Neo4j 엣지에서 스킬 추출 (없으면 profile_summary 기반)
    # node_idf 기반 희소성
    cur = conn.cursor()
    cur.execute(
        "SELECT profile_summary FROM candidates WHERE id=?", (cid,))
    row = cur.fetchone()
    summary = row[0] if row else ''

    # 현재 보유 스킬 추출
    candidate_skills = []
    for key, val in CANONICAL_MAP.items():
        if key.lower() in (summary or '').lower():
            if val not in candidate_skills:
                candidate_skills.append(val)
        if len(candidate_skills) >= 10:
            break

    skill_rarity_avg = 0.5
    if candidate_skills:
        rarities = [get_skill_rarity(s, 2022, node_idf)
                    for s in candidate_skills[:5]]
        skill_rarity_avg = sum(rarities) / len(rarities)

    combo_rarity = get_combo_rarity(
        candidate_skills[:3], conn, node_idf) if candidate_skills else 0.5

    tech_score = round(
        skill_rarity_avg * 0.6 + combo_rarity * 0.4, 3)

    # ── 4. Evidence Signal ──
    evidence = get_evidence_signal(raw_text)

    # ── 최종 CEI 점수 ──
    # 데이터 있는 것만 평균 (없는 것은 제외)
    scores = {
        'company': company_score * comp_signal.get('timing_score', 0.5),
        'tech': tech_score,
        'tenure': tenure_score,
        'evidence': evidence['completeness'],
    }

    overall = sum(scores.values()) / len(scores)

    # 신뢰도 계산
    confidence = (
        comp_signal.get('confidence', 0.5) * 0.4 +
        evidence['completeness'] * 0.4 +
        (0.8 if careers else 0.3) * 0.2
    )

    cei = {
        "company_signal": {
            "tier": comp_signal.get('tier', 'B'),
            "timing": comp_signal.get('timing_score', 0.5),
            "domain_relevance": comp_signal.get('domain_relevance', 0.5),
            "summary": comp_signal.get('company_summary', company),
        },
        "tenure_signal": tenure_sig,
        "tech_signal": {
            "skill_rarity": round(skill_rarity_avg, 3),
            "combo_rarity": round(combo_rarity, 3),
            "top_skills": candidate_skills[:5],
        },
        "evidence_signal": evidence,
        "scores": scores,
        "overall_cei": round(overall, 3),
        "confidence": round(confidence, 3),
        "data_completeness": evidence['completeness'],
        "inference_flag": evidence['completeness'] < 0.4,
        "generated_at": datetime.now().isoformat(),
    }

    return cei
