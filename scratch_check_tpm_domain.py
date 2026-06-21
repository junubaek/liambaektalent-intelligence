import sys
import os

sys.stdout.reconfigure(encoding='utf-8')
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT_DIR)

from jd_compiler import api_search_v9

# Let's inspect the prompt parsing logic inside jd_compiler by mimicking it.
prompt = 'Technical Program Manager'
query_lower = prompt.lower()

# Let's print out all keywords defined in jd_compiler to see where it matches
from jd_compiler import (
    SEMI_KEYWORDS, EMBEDDED_KEYWORDS, AI_KEYWORDS, MARKETING_KEYWORDS,
    PO_KEYWORDS, SW_KEYWORDS, HR_KEYWORDS, DESIGN_KEYWORDS,
    CTO_KEYWORDS, CFO_KEYWORDS, KAFKA_KEYWORDS
)

print("SEMI MATCH:", [k for k in SEMI_KEYWORDS if k in query_lower])
print("EMBEDDED MATCH:", [k for k in EMBEDDED_KEYWORDS if k in query_lower])
print("AI MATCH:", [k for k in AI_KEYWORDS if k in query_lower])
print("MARKETING MATCH:", [k for k in MARKETING_KEYWORDS if k in query_lower])
print("PO MATCH:", [k for k in PO_KEYWORDS if k in query_lower])
print("SW MATCH:", [k for k in SW_KEYWORDS if k in query_lower])
print("HR MATCH:", [k for k in HR_KEYWORDS if k in query_lower])
print("DESIGN MATCH:", [k for k in DESIGN_KEYWORDS if k in query_lower])
print("CTO MATCH:", [k for k in CTO_KEYWORDS if k in query_lower])
print("CFO MATCH:", [k for k in CFO_KEYWORDS if k in query_lower])
print("KAFKA MATCH:", [k for k in KAFKA_KEYWORDS if k in query_lower])

# Let's see what query_domain is mapped
query_domain = 'general'
if any(k in query_lower for k in SEMI_KEYWORDS):
    query_domain = 'semiconductor'
elif any(k in query_lower for k in EMBEDDED_KEYWORDS):
    query_domain = 'embedded'
elif any(k in query_lower for k in AI_KEYWORDS):
    query_domain = 'ai'
elif any(k in query_lower for k in MARKETING_KEYWORDS):
    query_domain = 'marketing'
elif any(k in query_lower for k in PO_KEYWORDS):
    query_domain = 'product'
elif any(k in query_lower for k in SW_KEYWORDS):
    query_domain = 'sw'
elif any(k in query_lower for k in HR_KEYWORDS):
    query_domain = 'hr'
elif any(k in query_lower for k in DESIGN_KEYWORDS):
    query_domain = 'design'
elif any(k in query_lower for k in CTO_KEYWORDS):
    query_domain = 'cto'
elif any(k in query_lower for k in CFO_KEYWORDS):
    query_domain = 'cfo'
elif any(k in query_lower for k in KAFKA_KEYWORDS):
    query_domain = 'data_infra'

print("\nMAPPED DOMAIN:", query_domain)
