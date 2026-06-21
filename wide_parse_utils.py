# wide_parse_utils.py
"""Utility functions for extended parsing of resumes.
   - detect_company_type: determines if a company is a big company or a startup.
   Returns a tuple (has_big_company, has_startup) where each is 1 (True) or 0 (False).
   Simple keyword based detection.
"""

def detect_company_type(company_name: str):
    """Detect whether the given company name corresponds to a big company or a startup.
    Returns two integers (has_big_company, has_startup).
    """
    if not company_name:
        return 0, 0
    name = company_name.lower()
    big_keywords = [
        "samsung", "lg", "hyundai", "sk", "kt", "naver", "coupang", "kakao",
        "lotte", "daewoo", "posco", "gs", "hanwha", "samsung electro", "samsung sds"
    ]
    startup_keywords = ["startup", "inc", "ltd", "corp", "co.", "co", "limited", "ventures", "tech", "ai", "lab"]
    has_big = any(k in name for k in big_keywords)
    has_startup = any(k in name for k in startup_keywords)
    if has_big:
        has_startup = 0
    return int(has_big), int(has_startup)
