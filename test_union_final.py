import sys
import logging
sys.stdout.reconfigure(line_buffering=True)
sys.stderr.reconfigure(line_buffering=True)
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

sys.path.append('C:/Users/cazam/Downloads/이력서자동분석검색시스템')

import jd_compiler

print("==== Starting final union tests ====")

try:
    print("Testing SCM물류...")
    res1 = jd_compiler.api_search_v8('SCM 물류 담당')
    print(f"Total SCM: {res1.get('total')}")
except Exception as e:
    print(f"Error SCM: {e}")

try:
    print("Testing ESG...")
    res2 = jd_compiler.api_search_v8('ESG 담당자')
    print(f"Total ESG: {res2.get('total')}")
except Exception as e:
    print(f"Error ESG: {e}")

sys.exit(0)
