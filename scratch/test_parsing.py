import sys, os
sys.stdout.reconfigure(encoding='utf-8')
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT_DIR)
os.chdir(ROOT_DIR)

from jd_compiler import parse_jd_to_json

res = parse_jd_to_json("General Affairs Manager")
print("Extracted conditions:")
for c in res.get('conditions', []):
    print(f" - {c['skill']} (source: {c['source']})")
