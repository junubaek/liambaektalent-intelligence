import json
from google import genai
from google.genai import types

with open("secrets.json", "r", encoding="utf-8") as f:
    secrets = json.load(f)
client = genai.Client(api_key=secrets["GEMINI_API_KEY"])

SYSTEM_INSTRUCTION = "You are an assistant."

print("Trying cache...")
try:
    cache = client.caches.create(
        model="gemini-2.5-flash",
        config=types.CreateCachedContentConfig(
            system_instruction=SYSTEM_INSTRUCTION,
            contents=[types.Content(role="user", parts=[types.Part.from_text(text="Placeholder")])],
            ttl="3600s",
        )
    )
    print(f"Success: {cache.name}")
except Exception as e:
    print(f"Failed: {e}")
