from jd_compiler import api_search_v9
import json

r = api_search_v9("Java Spring Boot RESTful Web Services", seniority="All")
print(json.dumps(r['matched'][:3], indent=2, ensure_ascii=False))
