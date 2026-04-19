import json
import google.generativeai as genai
import datetime

with open("secrets.json", "r", encoding="utf-8") as f:
    secrets = json.load(f)
genai.configure(api_key=secrets["GEMINI_API_KEY"])

prompt = """
이력서 텍스트에서 후보자가 실제로 수행한 행위를 추출해줘.
"""

try:
    print("Testing caching for models/gemini-1.5-flash")
    cache = genai.caching.CachedContent.create(
        model="models/gemini-1.5-flash",
        system_instruction="You are a strict resume parser.",
        contents=[prompt],
        ttl=datetime.timedelta(minutes=60)
    )
    print(f"Cache created! {cache.name}")
except Exception as e:
    print(f"Failed: {e}")
