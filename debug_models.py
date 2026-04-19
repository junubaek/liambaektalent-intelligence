import google.generativeai as genai
GEMINI_API_KEY = "AIzaSyCnMTVMuQ2673Br1o31h5JpSpxK_bIpYkE"
genai.configure(api_key=GEMINI_API_KEY)
for m in genai.list_models():
    if 'generateContent' in m.supported_generation_methods:
        print(m.name)
