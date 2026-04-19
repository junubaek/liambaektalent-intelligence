import sys
import logging
sys.path.append('C:/Users/cazam/Downloads/이력서자동분석검색시스템')

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

logger.info("Importing jd_compiler...")
from jd_compiler import api_search_v8

queries = ['M&A 담당자 찾아줘', '브랜드 마케터', '사업개발 BD']

for q in queries:
    logger.info(f"--- Testing Query: {q} ---")
    try:
        res = api_search_v8(prompt=q)
        logger.info(f"Found: {res.get('count', 0)} candidates")
    except Exception as e:
        logger.error(f"Error: {e}")
