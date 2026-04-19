"""
Antigravity Search Engine v5.1
notion-client 3.0.0 호환 수정본

변경사항:
- notion-client 3.0.0에서 databases.query() → databases.query(**kwargs) 동일하나
  Client 초기화 방식 및 async 처리 방식 변경 대응
- 에러 메시지를 명확하게 출력하도록 개선
- 모든 Notion API 호출을 단일 함수로 래핑
"""

import re
import json
import os
from typing import Optional

# ── notion-client 버전 호환 처리 ──────────────────────────────
try:
    from notion_client import Client
    from notion_client.errors import APIResponseError
    NOTION_CLIENT_AVAILABLE = True
except ImportError:
    NOTION_CLIENT_AVAILABLE = False
    print("[Warning] notion-client 미설치. pip install notion-client")

# Load secrets from local file for runtime instead of env vars
try:
    with open(os.path.join(os.path.dirname(os.path.dirname(__file__)), "secrets.json"), "r") as f:
        _secrets = json.load(f)
except FileNotFoundError:
    _secrets = {}

NOTION_TOKEN = _secrets.get("NOTION_API_KEY", "")
NOTION_DB_ID = _secrets.get("NOTION_DATABASE_ID", "")
GEMINI_API_KEY = _secrets.get("GEMINI_API_KEY", "")

# notion-client 3.0.0 Client 초기화
# 2.x: Client(auth=token)
# 3.0: Client(auth=token) — 동일하나 내부 httpx 기반으로 변경
def get_notion_client():
    if not NOTION_CLIENT_AVAILABLE:
        raise RuntimeError("notion-client가 설치되지 않았습니다.")
    if not NOTION_TOKEN:
        raise RuntimeError("NOTION_TOKEN 환경변수가 설정되지 않았습니다.")
    return Client(auth=NOTION_TOKEN)


# ─────────────────────────────────────────────────────────────
# Notion API 호출 래퍼 — 버전 호환 + 에러 처리
# ─────────────────────────────────────────────────────────────

def notion_query_raw(filter_obj: dict = None, page_size: int = 200) -> list[dict]:
    """
    Notion DB 쿼리 — notion-client 3.0.0 호환
    
    3.0.0 주요 변경:
    - 동기 Client는 동일하게 사용 가능
    - AsyncClient가 별도로 분리됨
    - APIResponseError 처리 방식 동일
    """
    try:
        client = get_notion_client()
        
        params = {
            "database_id": NOTION_DB_ID,
            "page_size": page_size,
        }
        if filter_obj:
            params["filter"] = filter_obj

        # 페이지네이션 처리 (200건 이상일 경우)
        all_results = []
        has_more = True
        next_cursor = None

        # fallback using raw HTTP requests to bypass notion-client 3.0.0 bugs
        import requests
        url = f"https://api.notion.com/v1/databases/{NOTION_DB_ID}/query"
        headers = {
            "Authorization": f"Bearer {NOTION_TOKEN}",
            "Notion-Version": "2022-06-28",
            "Content-Type": "application/json"
        }
        
        while has_more and len(all_results) < page_size:
            if next_cursor:
                params["start_cursor"] = next_cursor

            # Extract database_id if it exists to prevent validation error
            payload = params.copy()
            if "database_id" in payload:
                del payload["database_id"]
                
            # Notion API max page_size default/max is 100.
            # Passing 2000 or 3500 can cause undocumented timeouts/truncations.
            payload["page_size"] = min(100, page_size - len(all_results))

            http_resp = requests.post(url, headers=headers, json=payload)
            
            if http_resp.status_code != 200:
                print(f"[Notion API] HTTP Fallback Error: {http_resp.text}")
                break
                
            response = http_resp.json()
            results  = response.get("results", [])
            all_results.extend(results)

            has_more    = response.get("has_more", False)
            next_cursor = response.get("next_cursor")

            # page_size 초과 방지
            if len(all_results) >= page_size:
                break

        return [parse_notion_page(p) for p in all_results[:page_size]]

    except Exception as e:
        # 에러 유형별 메시지
        err = str(e)
        if "unauthorized" in err.lower() or "401" in err:
            print(f"[Notion API] 인증 오류 — NOTION_TOKEN 확인 필요: {e}")
        elif "object_not_found" in err.lower() or "404" in err:
            print(f"[Notion API] DB를 찾을 수 없음 — NOTION_DB_ID 확인 필요: {e}")
        elif "validation_error" in err.lower() or "400" in err:
            print(f"[Notion API] 필터 형식 오류: {e}")
            print(f"  → 전달된 filter: {json.dumps(filter_obj, ensure_ascii=False, indent=2)}")
        else:
            print(f"[Notion API] 알 수 없는 오류: {e}")
        return []


def parse_notion_page(page: dict) -> dict:
    """Notion 페이지 → 검색용 딕셔너리"""
    props = page.get("properties", {})

    def get_title(p):
        return "".join(t.get("plain_text", "") for t in p.get("title", []))

    def get_multi_select(p):
        return [s.get("name", "") for s in p.get("multi_select", [])]

    def get_rich_text(p):
        return "".join(t.get("plain_text", "") for t in p.get("rich_text", []))

    def get_select(p):
        s = p.get("select")
        return s.get("name", "") if s else ""

    # 현직무: 여러 필드명 시도 (스키마 불일치 방어)
    position = (
        get_select(props.get("현직무", {})) or
        get_rich_text(props.get("포지션", {})) or
        get_rich_text(props.get("position", {})) or
        get_rich_text(props.get("Position", {})) or
        ""
    )

    return {
        "id":                   page.get("id", ""),
        "notion_url":           page.get("url", ""),
        "이름":                 get_title(props.get("파일명", {})),
        "name_kr":              get_rich_text(props.get("Name", {})),
        "email":                props.get("이메일", {}).get("email", ""),
        "phone":                props.get("전화번호", {}).get("phone_number", ""),
        "Main Sectors":         get_multi_select(props.get("Main Sectors", {})),
        "Sub Sectors":          get_multi_select(props.get("Sub Sectors", {})),
        "Functional Patterns":  get_multi_select(props.get("Functional Patterns", {})),
        "Context Tags":         get_rich_text(props.get("Context Tags", {})),
        "Experience Summary":   get_rich_text(props.get("간단 프로필 요약", {})) or get_rich_text(props.get("간단프로필", {})) or get_rich_text(props.get("Experience Summary", {})),
        "현직무":               position,
        "Seniority Bucket":     get_select(props.get("Seniority Bucket", {})),
        "최근직장":             get_rich_text(props.get("최근직장", {})),
    }


# ─────────────────────────────────────────────────────────────
# SYNONYM_GROUPS + REVERSE_INDEX
# ─────────────────────────────────────────────────────────────

SYNONYM_GROUPS = [
    ["데이터 분석가", "data analyst", "데이터 분석", "da"],
    ["데이터 엔지니어", "data engineer", "de"],
    ["데이터 사이언티스트", "data scientist", "ds", "머신러닝 엔지니어"],
    ["데이터", "data", "데이타"],
    ["백엔드", "backend", "be", "서버 개발", "BE(서버)"],
    ["프론트엔드", "frontend", "fe", "프론트", "FE(웹)"],
    ["풀스택", "fullstack", "full stack"],
    ["devops", "데브옵스", "sre", "인프라", "DevOps_SRE"],
    ["모바일", "mobile", "ios", "android"],
    ["ai", "인공지능", "artificial intelligence"],
    ["머신러닝", "machine learning", "ml"],
    ["딥러닝", "deep learning", "dl"],
    ["nlp", "자연어처리", "natural language processing"],
    ["mlops", "serving", "엔지니어(Serving/MLOps)"],
    ["fp&a", "재무기획", "재무 기획", "financial planning", "FP&A(경영분석)", "경영분석"],
    ["재무", "finance", "파이낸스", "재무회계"],
    ["회계", "accounting", "cpa", "회계사(CPA)"],
    ["ir", "investor relations", "IR"],
    ["m&a", "merger", "acquisition", "인수합병", "M&A"],
    ["ipo", "상장", "기업공개", "예비심사"],
    ["투자담당자", "investment", "vc", "pe", "벤처캐피탈"],
    ["hr", "인사", "인사관리", "피플"],
    ["채용", "ta", "talent acquisition", "리크루팅", "채용(TA)"],
    ["보상기획", "c&b", "compensation", "평가보상(C&B)"],
    ["노무", "er", "employee relations", "노무(ER)"],
    ["인사기획", "hrbp", "인사전략"],
    ["마케팅", "marketing"],
    ["퍼포먼스 마케팅", "performance marketing", "그로스", "roas", "퍼포먼스"],
    ["브랜드", "brand", "브랜딩"],
    ["pr", "홍보", "언론홍보", "언론홍보(PR)", "public relations"],
    ["콘텐츠", "content", "인플루언서"],
    ["pm", "po", "product manager", "product owner", "서비스 기획",
     "Product Owner(PO)", "Project Manager(PM)"],
    ["uiux", "ui", "ux", "UIUX"],
    ["영업", "sales", "세일즈"],
    ["b2b", "기업영업", "법인영업", "B2B영업"],
    ["해외영업", "global sales", "international sales"],
    ["기술영업", "pre-sales", "기술영업(Pre-sales)"],
    ["전략", "strategy", "경영기획", "전략_경영기획"],
    ["신사업", "new business", "사업개발", "신사업 발굴 및 런칭"],
    ["반도체", "semiconductor"],
    ["hw", "하드웨어", "hardware", "HW(SoC; RTL)"],
    ["임베디드", "embedded", "펌웨어", "firmware"],
    ["회로설계", "circuit design", "rtl", "pcb", "회로설계(PCB)"],
    ["보안", "security", "정보보안", "정보보안(인프라/인증)"],
    ["개인정보보호", "cpo", "privacy", "개인정보보호(CPO; 규제 대응)"],
    ["scm", "공급망", "supply chain", "물류", "SCM(수요예측/공급망)"],
    ["구매", "procurement", "소싱", "sourcing"],
    ["법무", "legal", "컴플라이언스"],
]


def build_reverse_index(groups: list) -> dict:
    index = {}
    for i, group in enumerate(groups):
        for term in group:
            full = term.lower()
            index.setdefault(full, set()).add(i)
            for token in full.split():
                if len(token) >= 2:
                    index.setdefault(token, set()).add(i)
    return index

# 앱 시작 시 1회 빌드
REVERSE_INDEX = build_reverse_index(SYNONYM_GROUPS)


def _is_partial_match(query: str, key: str) -> bool:
    if re.match(r'^[a-z]{1,2}$', query):
        return query == key
    if re.search(r'[a-z]', query):
        pattern = r'\b' + re.escape(query) + r'\b'
        return bool(re.search(pattern, key))
    return query in key or key in query


def expand_query(user_input: str) -> list[str]:
    q = user_input.strip().lower()
    matched_groups = set()

    if q in REVERSE_INDEX:
        matched_groups.update(REVERSE_INDEX[q])

    if not matched_groups:
        for key, group_ids in REVERSE_INDEX.items():
            if _is_partial_match(q, key):
                matched_groups.update(group_ids)

    if not matched_groups:
        return [user_input]

    expanded = {user_input}
    for gid in matched_groups:
        expanded.update(SYNONYM_GROUPS[gid])
        
    result = list(expanded)
    if user_input in result:
        result.remove(user_input)
    return [user_input] + result


# ─────────────────────────────────────────────────────────────
# Notion 필터 빌드
# ─────────────────────────────────────────────────────────────

SHORT_ACRONYMS = {
    "da", "fe", "be", "de", "ds", "pm", "po",
    "ta", "ir", "hr", "ml", "dl", "cv", "sre",
    "cpa", "vc", "pe", "ip",
}

SEARCH_PROPS = [
    ("이름",                "title"),
    ("Main Sectors",        "multi_select"),
    ("Sub Sectors",         "multi_select"),
    ("Functional Patterns", "rich_text"),
    ("Context Tags",        "rich_text"),
    ("Experience Summary",  "rich_text"),  # v5.1: Summary도 1차 검색에 포함
]


def build_notion_filter(
    main_sectors: list[str] = None,
    sub_sectors:  list[str] = None,
    search_terms: list[str] = None,
    seniority:    str = "All",
    exclude:      list[str] = None,
) -> dict:
    main_sectors = main_sectors or []
    sub_sectors  = sub_sectors  or []
    search_terms = search_terms or []

    or_conditions = []

    # Sub Sectors 직접 매칭
    for ss in sub_sectors:
        or_conditions.append({
            "property": "Sub Sectors",
            "multi_select": {"contains": ss}
        })

    # 동의어 확장된 검색어
    for kw in search_terms:
        kw_lower = kw.lower()
        for prop, ptype in SEARCH_PROPS:
            # 짧은 약어는 태그에서만
            if kw_lower in SHORT_ACRONYMS and ptype not in ("multi_select",):
                continue
            if ptype == "title":
                or_conditions.append({"property": prop, "title": {"contains": kw}})
            elif ptype == "multi_select":
                or_conditions.append({"property": prop, "multi_select": {"contains": kw}})
            elif ptype == "rich_text":
                or_conditions.append({"property": prop, "rich_text": {"contains": kw}})

    and_conditions = []

    # Main Sectors (사이드바 선택)
    for sector in main_sectors:
        and_conditions.append({
            "property": "Main Sectors",
            "multi_select": {"contains": sector}
        })

    # 연차
    if seniority and seniority != "All":
        sen_map = {
            "신입~3년": "Junior",
            "4~6년": "Middle",
            "7년 이상": "Senior",
            "6년 이상": "Senior",
            "Junior": "Junior",
            "Middle": "Middle",
            "Senior": "Senior",
        }
        mapped_sen = sen_map.get(seniority, seniority)
        and_conditions.append({
            "property": "Seniority Bucket",
            "select": {"equals": mapped_sen}
        })

    # 키워드 OR 조건
    if or_conditions:
        if len(or_conditions) > 100:
            print(f"[Warning] OR 조건 100개 초과. 최대 100개로 제한됨 (원래 개수: {len(or_conditions)}).")
            or_conditions = or_conditions[:100]
        and_conditions.append({"or": or_conditions})

    if not and_conditions:
        return {}  # 조건 없으면 전체
    if len(and_conditions) == 1:
        return and_conditions[0]
    return {"and": and_conditions}


# ─────────────────────────────────────────────────────────────
# Fine Filter + Context Score
# ─────────────────────────────────────────────────────────────

FIELD_WEIGHTS = {
    "현직무":               10,
    "Sub Sectors":           8,
    "Main Sectors":          6,
    "Functional Patterns":   5,
    "Context Tags":          3,
    "Experience Summary":    2,
    "이름":                  1,
}

# v5.1: 임계값 완화
MATCHED_THRESHOLD = 5   # 기존 8 → 5
NEARBY_THRESHOLD  = 1   # 기존 3 → 1


def build_target_text(c: dict) -> str:
    parts = [
        c.get("현직무", ""),
        " ".join(c.get("Main Sectors", [])),
        " ".join(c.get("Sub Sectors", [])),
        " ".join(c.get("Functional Patterns", [])),
        c.get("Context Tags", ""),
        c.get("Experience Summary", ""),
        c.get("이름", ""),
    ]
    return " ".join(filter(None, parts)).lower()


def _regex_match(keyword: str, target: str) -> bool:
    kw = keyword.lower()
    if re.search(r'[a-zA-Z]', kw):
        pattern = r'\b' + re.escape(kw) + r'\b'
        return bool(re.search(pattern, target))
    return kw in target


def calc_score(
    c: dict,
    sub_sectors_from_parse: list[str],
    required_groups:        list[list[str]],
    preferred_groups:       list[list[str]],
    pattern_groups:         list[list[str]],
) -> int:
    score = 0
    field_values = {
        "현직무":               c.get("현직무", "").lower(),
        "Sub Sectors":          " ".join(c.get("Sub Sectors", [])).lower(),
        "Main Sectors":         " ".join(c.get("Main Sectors", [])).lower(),
        "Functional Patterns":  " ".join(c.get("Functional Patterns", [])).lower(),
        "Context Tags":         c.get("Context Tags", "").lower(),
        "Experience Summary":   c.get("Experience Summary", "").lower(),
        "이름":                 c.get("이름", "").lower(),
    }

    # Sub Sectors 직접 매칭 (최강 신호)
    for ss in sub_sectors_from_parse:
        if ss in c.get("Sub Sectors", []):
            score += 10

    # Required / Pattern / Preferred — 필드 가중치 적용
    def score_groups(groups, weight_multiplier=1.0):
        s = 0
        for group in groups:
            for kw in group:
                for field, value in field_values.items():
                    if _regex_match(kw, value):
                        s += int(FIELD_WEIGHTS.get(field, 1) * weight_multiplier)
                        break  # 같은 필드 중복 방지
        return s

    score += score_groups(required_groups,  1.0)
    score += score_groups(pattern_groups,   0.7)
    score += score_groups(preferred_groups, 0.4)

    return score


def fine_filter_and_score(
    candidates:             list[dict],
    sub_sectors_from_parse: list[str],
    required_groups:        list[list[str]],
    preferred_groups:       list[list[str]],
    pattern_groups:         list[list[str]],
    exclude:                list[str],
    strict_required:        bool = False,  # v5.1: 기본값 False로 완화
) -> list[dict]:
    """
    strict_required=False (기본):
        Required 조건 미충족 시 탈락 없음 — Score만 낮아짐
    strict_required=True:
        Required 조건 중 하나라도 없으면 탈락
    """
    results = []

    for c in candidates:
        target = build_target_text(c)

        # Exclude 필터
        if any(_regex_match(ex, target) for ex in exclude):
            continue

        # Required AND 강제 (strict 모드일 때만)
        if strict_required and required_groups:
            all_match = all(
                any(_regex_match(kw, target) for kw in group)
                for group in required_groups
            )
            if not all_match:
                continue

        score = calc_score(
            c,
            sub_sectors_from_parse,
            required_groups,
            preferred_groups,
            pattern_groups,
        )

        c["_score"] = score
        results.append(c)

    results.sort(key=lambda x: x["_score"], reverse=True)
    return results


# ─────────────────────────────────────────────────────────────
# 유사 Sub Sectors 매핑
# ─────────────────────────────────────────────────────────────

SIMILAR_SUB_SECTORS = {
    "언론홍보(PR)":                    ["마케팅기획", "브랜드", "콘텐츠(인플루언서 협업/제휴 포함)"],
    "FP&A(경영분석)":                  ["재무회계", "전략_경영기획", "IR"],
    "IR":                              ["FP&A(경영분석)", "M&A", "투자담당자(Investment/VC/PE)"],
    "M&A":                             ["IR", "투자담당자(Investment/VC/PE)", "전략_경영기획"],
    "투자담당자(Investment/VC/PE)":    ["IR", "M&A", "FP&A(경영분석)"],
    "채용(TA)":                        ["인사기획", "평가보상(C&B)"],
    "데이터분석가":                    ["데이터사이언티스트", "데이터엔지니어"],
    "데이터사이언티스트":              ["데이터분석가", "리서쳐(모델링)", "엔지니어(Serving/MLOps)"],
    "데이터엔지니어":                  ["데이터분석가", "DevOps_SRE", "인프라_Cloud"],
    "BE(서버)":                        ["DevOps_SRE", "인프라_Cloud"],
    "FE(웹)":                          ["UIUX", "웹", "Mobile(iOS; Android)"],
    "전략_경영기획":                   ["신사업 발굴 및 런칭", "Business Operation(프로세스 효율화)"],
    "퍼포먼스":                        ["그로스", "마케팅기획"],
    "브랜드":                          ["마케팅기획", "콘텐츠(인플루언서 협업/제휴 포함)", "언론홍보(PR)"],
    "정보보안(인프라/인증)":           ["개인정보보호(CPO; 규제 대응)", "컴플라이언스"],
    "B2B영업":                         ["기술영업(Pre-sales)", "해외영업", "영업기획"],
    "회로설계(PCB)":                   ["HW(SoC; RTL)", "임베디드", "FW(컨트롤러)"],
    "재무회계":                        ["FP&A(경영분석)", "세무", "내부통제_감사"],
}


def suggest_alternatives(
    main_sectors:    list[str],
    sub_sectors:     list[str],
    seniority:       str,
    required_groups: list[list[str]],
    preferred_groups:list[list[str]],
    pattern_groups:  list[list[str]],
    exclude:         list[str],
) -> dict:
    """결과 없을 때 단계별 조건 완화 → 대안 제시"""

    # 1단계: Required 하나씩 제거
    for i, removed in enumerate(required_groups):
        relaxed = [g for j, g in enumerate(required_groups) if j != i]
        flat    = [t for g in relaxed + preferred_groups + pattern_groups for t in g]

        f = build_notion_filter(main_sectors, sub_sectors, flat, seniority, exclude)
        raw = notion_query_raw(f, page_size=50)
        filtered = fine_filter_and_score(
            raw, sub_sectors, relaxed,
            preferred_groups, pattern_groups, exclude,
            strict_required=False,
        )
        scored = [c for c in filtered if c["_score"] >= NEARBY_THRESHOLD]
        if scored:
            label = removed[0] if removed else ""
            return {
                "type":    "relaxed_required",
                "message": f"'{label}' 조건을 제외하면 {len(scored)}명이 있습니다.",
                "results": scored[:10],
            }

    # 2단계: 유사 Sub Sectors
    similar = []
    for ss in sub_sectors:
        similar.extend(SIMILAR_SUB_SECTORS.get(ss, []))
    similar = list(set(similar) - set(sub_sectors))

    if similar:
        flat = [t for g in preferred_groups + pattern_groups for t in g]
        f    = build_notion_filter(main_sectors, similar, flat, seniority, exclude)
        raw  = notion_query_raw(f, page_size=50)
        if raw:
            return {
                "type":    "similar_sub_sector",
                "message": f"유사 직군 [{', '.join(similar[:3])}]으로 검색하면 {len(raw)}명이 있습니다.",
                "results": raw[:10],
            }

    # 3단계: Main Sectors 전체
    if main_sectors:
        f   = build_notion_filter(main_sectors, [], [], seniority)
        raw = notion_query_raw(f, page_size=50)
        if raw:
            label = ", ".join(main_sectors)
            return {
                "type":    "sector_only",
                "message": f"조건을 모두 제거하면 [{label}] 섹터에 {len(raw)}명이 있습니다.",
                "results": raw[:10],
            }

    return {
        "type":    "no_results",
        "message": "현재 DB에 해당 조건의 후보자가 없습니다.",
        "results": [],
    }


# ─────────────────────────────────────────────────────────────
# Gemini 파싱
# ─────────────────────────────────────────────────────────────

ALL_SUB_SECTORS = [
    "B2B영업", "BE(서버)", "Business Operation(프로세스 효율화)",
    "DBA(DBMS 운영; 성능 최적화; 보안)", "DevOps_SRE", "FAE_CE",
    "FE(웹)", "FP&A(경영분석)", "FW(컨트롤러)", "HW(SoC; RTL)",
    "IR", "M&A", "Mobile(iOS; Android)", "Product Owner(PO)",
    "Project Manager(PM)", "SCM(수요예측/공급망)", "SW(하단 드라이버)",
    "TPM", "UIUX", "개인정보보호(CPO; 규제 대응)", "공정(Yield/FAB)",
    "교육(L&D)", "구매", "그로스", "급여(Payroll)", "기구설계",
    "기술영업(Pre-sales)", "기타",
    "기획(AI Governance; DT; AT; AX 전략 설계)",
    "내부통제_감사", "노무(ER)", "데이터분석가", "데이터사이언티스트",
    "데이터엔지니어", "디자인 기획 및 시스템 구축", "로보틱스",
    "리서쳐(모델링)", "마케팅기획", "물류기획 및 프로세스 최적화",
    "변호사", "복리후생 운영", "브랜드", "상품기획(Selection)",
    "서비스기획(화면설계)", "세무", "소싱MD(해외 직소싱/원가)",
    "신사업 발굴 및 런칭", "언론홍보(PR)", "엔지니어(Serving/MLOps)",
    "영업MD(채널 매출 관리)", "영업기획", "영업지원", "웹",
    "유통망 관리", "인사기획", "인프라_Cloud", "일반법무", "임베디드",
    "자금", "자동화(PLC)",
    "자산관리(부동산; 법인 자산; IT 비품 구매 및 관리)",
    "재무회계", "전략_경영기획", "정보보안(인프라/인증)", "제품",
    "지적재산권(IP)", "채용(TA)", "컴플라이언스",
    "콘텐츠(인플루언서 협업/제휴 포함)",
    "퍼포먼스", "평가보상(C&B)", "해외영업", "회계사(CPA)",
    "회로설계(PCB)", "투자담당자(Investment/VC/PE)",
]

GEMINI_PARSE_PROMPT = """
당신은 헤드헌팅 DB 검색 파라미터 추출 전문가입니다.

[DB Sub Sectors 목록 — 반드시 이 목록에서만 선택]
{sub_sectors_list}

[헤드헌터 프롬프트]
{prompt}

[추출 규칙]
1. sub_sectors: 위 목록에서 매핑 가능한 직무만. 목록 외 값 절대 금지.
2. pattern_keywords: DB에 기록됐을 법한 팩트 기반 키워드만.
   금지: "주도적", "열정적", "탁월한", "성장 가능성" 등 성향/태도 표현
   허용: "IPO", "시리즈 C", "인하우스", "MSA", "대용량 트래픽"
3. exclude: 명시적 제외 조건.
4. gap_flags: DB 확인 불가 항목 (네트워크, 인맥, 주도성, 잠재력 → 여기로).
5. db_miss_risk: DB에서 찾기 어려울 수 있는 조건 (사전 경고용).

[출력 — JSON만, 마크다운 없음]
{{"sub_sectors":[""],"pattern_keywords":[""],"exclude":[""],"gap_flags":[""],"db_miss_risk":[""]}}
"""


def gemini_parse_prompt(prompt: str) -> dict:
    empty = {
        "sub_sectors": [], "pattern_keywords": [],
        "exclude": [], "gap_flags": [], "db_miss_risk": [],
    }
    if not prompt.strip():
        return empty

    try:
        import google.generativeai as genai
        genai.configure(api_key=GEMINI_API_KEY)
        # Use gemini-2.5-flash to avoid 404 from gemini-2.0-flash
        model = genai.GenerativeModel("gemini-2.5-flash")

        filled = GEMINI_PARSE_PROMPT.format(
            sub_sectors_list="\n".join(f"- {s}" for s in ALL_SUB_SECTORS),
            prompt=prompt,
        )
        response = model.generate_content(
            filled,
            generation_config={"temperature": 0.1},
        )
        raw = re.sub(r"```json|```", "", response.text.strip()).strip()
        result = json.loads(raw)

        # 빈 문자열 제거
        for key in result:
            if isinstance(result[key], list):
                result[key] = [v for v in result[key] if v and v.strip()]
        return result

    except json.JSONDecodeError as e:
        print(f"[Gemini] JSON 파싱 실패: {e}")
        return empty
    except Exception as e:
        print(f"[Gemini] 호출 실패: {e}")
        return empty


# ─────────────────────────────────────────────────────────────
# 메인 검색 함수
# ─────────────────────────────────────────────────────────────

def search_candidates(
    prompt:          str       = "",
    sectors:         list[str] = None,
    seniority:       str       = "All",
    required:        list[str] = None,
    preferred:       list[str] = None,
    strict_required: bool      = False,  # v5.1: 기본 False
) -> dict:
    """
    메인 검색 — v5.1

    변경:
    - strict_required 기본값 False (AND 강제 없음)
    - MATCHED_THRESHOLD 5로 완화
    - Experience Summary를 1차 Notion 검색에 포함
    - 에러 메시지 개선
    """
    sectors   = sectors   or []
    required  = required  or []
    preferred = preferred or []

    # Step 1: Gemini 파싱
    parsed = gemini_parse_prompt(prompt) if prompt.strip() else {
        "sub_sectors": [], "pattern_keywords": [],
        "exclude": [], "gap_flags": [], "db_miss_risk": [],
    }

    # Step 2: 쿼리 확장
    required_groups  = [expand_query(kw) for kw in required]
    preferred_groups = [expand_query(kw) for kw in preferred]
    pattern_groups   = [expand_query(kw) for kw in parsed.get("pattern_keywords", [])]

    all_terms = (
        [t for g in required_groups  for t in g] +
        [t for g in preferred_groups for t in g] +
        [t for g in pattern_groups   for t in g]
    )

    # Step 3: Notion 1차 추출
    f = build_notion_filter(
        main_sectors = sectors,
        sub_sectors  = parsed.get("sub_sectors", []),
        search_terms = all_terms,
        seniority    = seniority,
        exclude      = parsed.get("exclude", []),
    )
    raw = notion_query_raw(f, page_size=200)

    # Step 4: Fine Filter + Score
    scored = fine_filter_and_score(
        candidates             = raw,
        sub_sectors_from_parse = parsed.get("sub_sectors", []),
        required_groups        = required_groups,
        preferred_groups       = preferred_groups,
        pattern_groups         = pattern_groups,
        exclude                = parsed.get("exclude", []),
        strict_required        = strict_required,
    )

    # Step 5: 분류
    matched = [c for c in scored if c["_score"] >= MATCHED_THRESHOLD]
    nearby  = [c for c in scored if NEARBY_THRESHOLD <= c["_score"] < MATCHED_THRESHOLD]

    # Step 6: 결과 없으면 대안 제시
    alternative = None
    if not matched and not nearby:
        alternative = suggest_alternatives(
            main_sectors     = sectors,
            sub_sectors      = parsed.get("sub_sectors", []),
            seniority        = seniority,
            required_groups  = required_groups,
            preferred_groups = preferred_groups,
            pattern_groups   = pattern_groups,
            exclude          = parsed.get("exclude", []),
        )

    return {
        "matched":      matched,
        "nearby":       nearby,
        "alternative":  alternative,
        "gap_flags":    parsed.get("gap_flags", []),
        "db_miss_risk": parsed.get("db_miss_risk", []),
        "total":        len(matched) + len(nearby),
        "parsed":       parsed,
    }
