import google.generativeai as genai
GEMINI_API_KEY = "INSERT_YOUR_NEW_GEMINI_API_KEY_HERE"
genai.configure(api_key=GEMINI_API_KEY)
for m in genai.list_models():
    if 'generateContent' in m.supported_generation_methods:
        print(m.name)
