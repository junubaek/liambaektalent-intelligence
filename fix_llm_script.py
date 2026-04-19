with open('run_deep_repair_llm.py', 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace("from ai_talent_intelligence_system.scripts.gemini_utils import generate_json_with_gemini\n", "")

with open('run_deep_repair_llm.py', 'w', encoding='utf-8') as f:
    f.write(text)
    
print("Fixed import!")
