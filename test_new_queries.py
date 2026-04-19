import sys
import logging
sys.stdout.reconfigure(line_buffering=True)
sys.stderr.reconfigure(line_buffering=True)
logging.basicConfig(level=logging.ERROR) # reduce noise
logger = logging.getLogger(__name__)

sys.path.append('C:/Users/cazam/Downloads/이력서자동분석검색시스템')

import jd_compiler

queries = [
    "ESG 담당자",
    "컴플라이언스 담당자",
    "HR 인사기획 7년차",
    "특허 변호사",
    "SCM 물류 담당"
]

print("Starting search tests...")
for q in queries:
    try:
        res = jd_compiler.api_search_v8(prompt=q)
        total = res.get("total", 0)
        print(f"[{q}] -> {total} 명")
        if total == 0:
            print(f"  Missing edges: {res.get('missing_edges', 'Unknown')}")
            print(f"  Matched edges: {res.get('matched_edges', 'Unknown')}")
            # we can look closer if it's 0
    except Exception as e:
        print(f"[{q}] -> Error: {e}")
