import sys
import json
from jd_compiler import parse_jd_to_json

try:
    res = parse_jd_to_json("IPO/펀딩 대비 자금 담당자 6년차")
    print("OUTPUT_JSON_START")
    print(json.dumps(res, indent=2, ensure_ascii=False))
    print("OUTPUT_JSON_END")
except Exception as e:
    print(f"ERROR: {e}")
