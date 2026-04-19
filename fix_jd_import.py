import sys

with open("jd_compiler.py", "r", encoding="utf-8") as f:
    text = f.read()

# Replace any import with NODE_AFFINITY
if "NODE_AFFINITY" in text:
    text = text.replace("NODE_AFFINITY,", "")
    text = text.replace(", NODE_AFFINITY", "")
    text = text.replace("import NODE_AFFINITY", "import CANONICAL_MAP")

with open("jd_compiler.py", "w", encoding="utf-8") as f:
    f.write(text)
    
print("Fixed jd_compiler.py")
