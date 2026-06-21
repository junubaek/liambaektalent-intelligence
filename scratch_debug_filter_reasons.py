import json
import sqlite3
import sys
from jd_compiler import api_search_v9

sys.stdout.reconfigure(encoding='utf-8')

with open('secrets.json', encoding='utf-8') as f:
    secrets = json.load(f)

tests = [
    ('SCM logistics operations cost management', 'MIDDLE', '31f22567-1b6f-8152-93ca-ca5ab3080016', '유정한'),
    ('on-device AI inference embedded AI semiconductor', 'SENIOR', 'ba4abc09-302e-4fd4-ae93-b8af52aed567', '하현재'),
    ('healthcare AI computer vision deep learning medical imaging', 'MIDDLE', '32022567-1b6f-819f-b62e-fa5ecb02e3de', '김진영'),
    ('IPO IR strategic planning fundraising finance', 'SENIOR', '1c3e3279-b0c5-4661-9dcf-7fa929dd47bb', '김진호'),
]

conn = sqlite3.connect('candidates.db')
cur = conn.cursor()

# We patch jd_compiler inside python memory to intercept
# Let's inspect the query domain and min_years by running a mini simulation of api_search_v9's parsing block

# Re-import to ensure it is clean
import httpx
from openai import OpenAI
openai_client = OpenAI(api_key=secrets['OPENAI_API_KEY'])

MEGA_PROMPT_CHECK = """입력된 채용 공고(JD) 또는 검색 쿼리를 분석하여 최적의 검색 조건 구조를 JSON으로 출력해.
반드시 아래의 JSON 구조만 출력할 것.

{{
  "min_years": 최소 경력 년수 숫자 (예: 5. 신입이거나 제한 없으면 0),
  "preferred_companies": ["우대 기업명 목록"]
}}
"""

for query, seniority, target_id, name in tests:
    print(f"\n--- Tracing {name} ({target_id}) for query: '{query}' ---")
    
    # 1. Get LLM parsed min_years
    res = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": MEGA_PROMPT_CHECK},
            {"role": "user", "content": query}
        ],
        temperature=0.0
    )
    raw = res.choices[0].message.content.replace("```json", "").replace("```", "").strip()
    parsed_query = json.loads(raw)
    min_years = parsed_query.get("min_years", 0)
    print(f"  Extracted min_years: {min_years}")
    
    # 2. Get query domain and allowed sectors
    query_lower = query.lower()
    SEMI_KEYWORDS = ['npu', 'soc', '반도체', 'rtl', 'fpga', 'asic', '칩', 'verilog', 'tape-out', 'tape out', 'ppa']
    EMBEDDED_KEYWORDS = ['임베', '커널', 'kernel', 'firmware', 'bsp', 'rtos', 'embedded']
    AI_KEYWORDS   = ['llm', 'ai ', '인공', 'ml ', '딥러닝', 'deep learning', 'gpu', 'inference', 'transformer', 'pytorch', 'mlops']
    SW_KEYWORDS   = ['백엔드', 'backend', '프론트', 'frontend', 'devops', '인프라', 'infra', 'kubernetes', 'docker', 'msa']
    MARKETING_KEYWORDS = ['마케팅', 'marketing', '브랜드', 'crm', 'growth']
    PO_KEYWORDS = ['product owner', 'po ', 'p.o.', '프로덕트', 'pm ', 'product manager']
    HR_KEYWORDS  = ['hr', '채용', '인사', '총무', 'general affairs']
    DESIGN_KEYWORDS = ['uiux', 'ui/ux', '디자이너', 'product design', 'figma']
    CTO_KEYWORDS = ['cto', 'chief technology']
    CFO_KEYWORDS = ['cfo', 'chief financial', '재무', '회계']
    KAFKA_KEYWORDS = ['kafka', '카프카', 'message queue']
    
    query_domain = 'general'
    if any(k in query_lower for k in SEMI_KEYWORDS): query_domain = 'semiconductor'
    elif any(k in query_lower for k in EMBEDDED_KEYWORDS): query_domain = 'embedded'
    elif any(k in query_lower for k in AI_KEYWORDS): query_domain = 'ai'
    elif any(k in query_lower for k in MARKETING_KEYWORDS): query_domain = 'marketing'
    elif any(k in query_lower for k in PO_KEYWORDS): query_domain = 'product'
    elif any(k in query_lower for k in SW_KEYWORDS): query_domain = 'sw'
    elif any(k in query_lower for k in HR_KEYWORDS): query_domain = 'hr'
    elif any(k in query_lower for k in DESIGN_KEYWORDS): query_domain = 'design'
    elif any(k in query_lower for k in CTO_KEYWORDS): query_domain = 'cto'
    elif any(k in query_lower for k in CFO_KEYWORDS): query_domain = 'cfo'
    elif any(k in query_lower for k in KAFKA_KEYWORDS): query_domain = 'data_infra'
    
    ALLOWED_SECTORS = {
        'semiconductor': {'Eng_Semi', 'Eng_Embedded', 'Eng_AI'},
        'embedded':      {'Eng_Embedded', 'Eng_Semi', 'Eng_HW', 'Eng_SW'},
        'ai':            {'Eng_AI', 'Eng_SW', 'Eng_Data', 'Eng_Semi', 'Eng_Embedded'},
        'marketing':     {'Marketing', 'Strategy', 'Product'},
        'product':       {'Product', 'Strategy', 'Eng_SW', 'Eng_AI'},
        'sw':            {'Eng_SW', 'Eng_AI', 'Eng_Data', 'Eng_Embedded'},
        'hr':            {'HR'},
        'design':        {'Product', 'Marketing'},
        'cto':           {'Eng_SW', 'Eng_AI', 'Product', 'Strategy'},
        'cfo':           {'Finance', 'Strategy'},
        'data_infra':    {'Eng_Data', 'Eng_SW', 'Eng_AI'},
        'general':       None
    }
    
    detected_domains = []
    if any(k in query_lower for k in SEMI_KEYWORDS): detected_domains.append('semiconductor')
    if any(k in query_lower for k in AI_KEYWORDS): detected_domains.append('ai')
    if any(k in query_lower for k in SW_KEYWORDS): detected_domains.append('sw')
    
    if len(detected_domains) > 1:
        allowed = set()
        for d in detected_domains:
            allowed |= ALLOWED_SECTORS.get(d, set())
    else:
        allowed = ALLOWED_SECTORS.get(query_domain)
        
    print(f"  Query Domain: {query_domain}, Detected Domains: {detected_domains}")
    print(f"  Allowed Sectors: {allowed}")
    
    # 3. Get candidate details from SQLite
    cur.execute("SELECT name_kr, total_years, sector FROM candidates WHERE id=?", (target_id,))
    row = cur.fetchone()
    c_name, c_years, c_sector = row
    primary_sector = c_sector.split(',')[0].strip() if c_sector else ''
    print(f"  Candidate Sector: {primary_sector}, Candidate Years: {c_years}")
    
    # Evaluate reasons
    is_filtered_sector = allowed is not None and primary_sector not in allowed
    is_filtered_years = min_years > 0 and c_years < min_years
    print(f"  -> Dropped by Sector filter? {is_filtered_sector}")
    print(f"  -> Dropped by Years filter? {is_filtered_years}")

conn.close()
