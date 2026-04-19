import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.stdout.reconfigure(encoding='utf-8')

import asyncio
from neo4j import GraphDatabase
import jd_compiler

print("--- 1. Query JD Parsing ---")
try:
    query = "6년차 이상 자금 담당자"
    print(f"Input Query: {query}")
    parsed_json = asyncio.run(jd_compiler.parse_jd_to_json(query))
    import json
    print(json.dumps(parsed_json, indent=2, ensure_ascii=False))
except Exception as e:
    print(f"Error parsing JD: {e}")
