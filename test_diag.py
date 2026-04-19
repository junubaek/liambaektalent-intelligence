# 검색 실패 원인 진단 스크립트

import os, re, json
from notion_client import Client

# Load secrets
with open("secrets.json", "r") as f:
    secrets = json.load(f)

NOTION_TOKEN = secrets.get("NOTION_API_KEY")
NOTION_DB_ID = secrets.get("NOTION_DATABASE_ID")
notion       = Client(auth=NOTION_TOKEN)

# ── 테스트 값 여기에 입력 ──────────────────────────────────
TEST_SECTORS   = ["마케팅 (Marketing)"]   # 사이드바 선택값
TEST_SENIORITY = "Senior"                 # 연차
TEST_REQUIRED  = ["PR"]                   # Required Keywords
TEST_PREFERRED = ["인하우스"]             # Preferred Keywords
TEST_PROMPT    = "IPO 대비 PR 경력자"     # 프롬프트
# ──────────────────────────────────────────────────────────

def raw_query(filter_obj=None, page_size=10):
    try:
        params = {"database_id": NOTION_DB_ID, "page_size": page_size}
        if filter_obj:
            params["filter"] = filter_obj
        res = notion.databases.query(**params)
        pages = res.get("results", [])
        return pages
    except Exception as e:
        print(f"  ❌ API 에러: {e}")
        return []

def page_to_text(page):
    props = page.get("properties", {})
    def ms(p):   return [s.get("name","") for s in p.get("multi_select",[])]
    def rt(p):   return "".join(t.get("plain_text","") for t in p.get("rich_text",[]))
    def ttl(p):  return "".join(t.get("plain_text","") for t in p.get("title",[]))
    def sel(p):  s=p.get("select"); return s.get("name","") if s else ""

    return {
        "이름":                ttl(props.get("이름",{})),
        "Main Sectors":        ms(props.get("Main Sectors",{})),
        "Sub Sectors":         ms(props.get("Sub Sectors",{})),
        "Functional Patterns": rt(props.get("Functional Patterns",{})),
        "Context Tags":        rt(props.get("Context Tags",{})),
        "Experience Summary":  rt(props.get("Experience Summary",{})),
        "현직무":              sel(props.get("현직무",{})) or rt(props.get("포지션",{})),
        "연차등급":            sel(props.get("연차등급",{})),
    }

def sep(title):
    print(f"\n{'─'*60}")
    print(f"  {title}")
    print('─'*60)

# ══════════════════════════════════════════════════════════════
# STEP 1: 필터 없이 전체 쿼리
# ══════════════════════════════════════════════════════════════
sep("STEP 1: 필터 없이 전체 쿼리 (최대 5건)")
pages = raw_query(page_size=5)
print(f"  결과: {len(pages)}건")
for p in pages:
    d = page_to_text(p)
    print(f"  → {d['이름']} | {d['Main Sectors']} | {d['Sub Sectors']}")

if not pages:
    print("  ❌ 전체 쿼리도 안 됨 → NOTION_TOKEN 또는 DB_ID 확인 필요")
    exit()

# ══════════════════════════════════════════════════════════════
# STEP 2: Main Sectors 필터만
# ══════════════════════════════════════════════════════════════
sep(f"STEP 2: Main Sectors 필터만 ({TEST_SECTORS})")
for sector in TEST_SECTORS:
    f = {"property": "Main Sectors", "multi_select": {"contains": sector}}
    pages = raw_query(f, page_size=5)
    print(f"  '{sector}' → {len(pages)}건")
    for p in pages:
        d = page_to_text(p)
        print(f"    → {d['이름']} | {d['Sub Sectors']}")

if not pages:
    # 실제 저장된 Main Sectors 값 확인
    print("\n  ⚠️  실제 저장된 Main Sectors 값 확인:")
    all_pages = raw_query(page_size=20)
    sectors_found = set()
    for p in all_pages:
        d = page_to_text(p)
        for s in d["Main Sectors"]:
            sectors_found.add(s)
    print(f"  DB에 있는 실제 Main Sectors: {sorted(sectors_found)}")
    print(f"  검색에 쓴 값: {TEST_SECTORS}")
    print("  → 값이 다르면 UI의 섹터 이름과 DB 저장값을 맞춰야 합니다")

# ══════════════════════════════════════════════════════════════
# STEP 3: 키워드 하나씩 단독 쿼리
# ══════════════════════════════════════════════════════════════
sep(f"STEP 3: Required Keywords 단독 쿼리")
for kw in TEST_REQUIRED:
    f1 = {"property": "Sub Sectors", "multi_select": {"contains": kw}}
    r1 = raw_query(f1, page_size=5)
    print(f"  Sub Sectors contains '{kw}' → {len(r1)}건")

    f2 = {"property": "Context Tags", "rich_text": {"contains": kw}}
    r2 = raw_query(f2, page_size=5)
    print(f"  Context Tags contains '{kw}' → {len(r2)}건")

    f3 = {"property": "Functional Patterns", "rich_text": {"contains": kw}}
    r3 = raw_query(f3, page_size=5)
    print(f"  Functional Patterns contains '{kw}' → {len(r3)}건")

    f4 = {"property": "Experience Summary", "rich_text": {"contains": kw}}
    r4 = raw_query(f4, page_size=5)
    print(f"  Experience Summary contains '{kw}' → {len(r4)}건")

    total = len(r1) + len(r2) + len(r3) + len(r4)
    if total == 0:
        print(f"\n  ⚠️  '{kw}'로 아무 필드에서도 안 나옴")

# ══════════════════════════════════════════════════════════════
# STEP 4: 섹터 + 키워드 AND 조합
# ══════════════════════════════════════════════════════════════
sep("STEP 4: 섹터 AND 키워드 조합")
for sector in TEST_SECTORS:
    for kw in TEST_REQUIRED:
        f = {
            "and": [
                {"property": "Main Sectors", "multi_select": {"contains": sector}},
                {"or": [
                    {"property": "Sub Sectors",         "multi_select": {"contains": kw}},
                    {"property": "Context Tags",         "rich_text":    {"contains": kw}},
                    {"property": "Functional Patterns",  "rich_text":    {"contains": kw}},
                    {"property": "Experience Summary",   "rich_text":    {"contains": kw}},
                ]}
            ]
        }
        pages = raw_query(f, page_size=5)
        print(f"  [{sector}] AND [{kw}] → {len(pages)}건")
        for p in pages:
            d = page_to_text(p)
            print(f"    → {d['이름']} | {d['Sub Sectors']}")

# ══════════════════════════════════════════════════════════════
# STEP 6: 연차 필터 확인
# ══════════════════════════════════════════════════════════════
sep(f"STEP 6: 연차 필터 확인 ('{TEST_SENIORITY}')")
f = {"property": "연차등급", "select": {"equals": TEST_SENIORITY}}
pages = raw_query(f, page_size=5)
print(f"  연차등급 = '{TEST_SENIORITY}' → {len(pages)}건")

if not pages:
    print("\n  ⚠️  연차 필터로 아무도 안 나옴")
    all_pages = raw_query(page_size=30)
    seniorities = set()
    for p in all_pages:
        d = page_to_text(p)
        if d["연차등급"]:
            seniorities.add(d["연차등급"])
    print(f"  DB에 있는 연차등급 값: {sorted(list(seniorities))}")
    print(f"  코드에서 쓴 값: '{TEST_SENIORITY}'")

sep("진단 완료 — 위 결과를 확인하세요")
