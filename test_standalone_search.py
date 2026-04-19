import sys
import logging
sys.stdout.reconfigure(line_buffering=True)
sys.stderr.reconfigure(line_buffering=True)
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

sys.path.append('C:/Users/cazam/Downloads/이력서자동분석검색시스템')

logger.info("Importing jd_compiler... please wait.")
import jd_compiler
logger.info("Import complete!")

queries = ["M&A 담당자 찾아줘", "브랜드 마케터", "사업개발 BD"]

for q in queries:
    logger.info(f"--- QUERY: {q} ---")
    try:
        res = jd_compiler.api_search_v8(prompt=q)
        total = res.get("total", 0)
        logger.info(f"Found {total} candidates for {q}")
        for r in res.get("matched", [])[:3]:
            logger.info(f"  - {r.get('name')} | {r.get('position')}")
    except Exception as e:
        logger.error(f"Error for {q}: {e}")
