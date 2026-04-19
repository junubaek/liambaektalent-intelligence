import json
import math

with open('temp_candidates.json', 'r', encoding='utf-8-sig') as f:
    data = json.load(f)

total_candidates = len(data.get('results', []))
empty_patterns = 0

for page in data.get('results', []):
    props = page.get('properties', {})
    patterns = props.get('Functional Patterns', {}).get('multi_select', [])
    if not patterns:
        empty_patterns += 1

print(f"Total Candidates: {total_candidates}")
print(f"Candidates without patterns: {empty_patterns}")
print(f"Completed Candidates: {total_candidates - empty_patterns}")

# Assuming our orchestrator processes ~100 per 40 mins (based on 429 delays)
if empty_patterns > 0:
    estimated_mins = empty_patterns * 0.4 
    print(f"Estimated time remaining: {math.ceil(estimated_mins)} minutes")
else:
    print(f"Estimated time remaining: 0 minutes")
