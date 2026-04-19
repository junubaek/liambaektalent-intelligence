import json

with open('temp_candidates.json', 'r', encoding='utf-8-sig') as f:
    data = json.load(f)

count = 0
empty_roles = 0
for page in data.get('results', []):
    props = page.get('properties', {})
    patterns = props.get('Functional Patterns', {}).get('multi_select', [])
    pattern_names = [p['name'] for p in patterns]
    
    if "General Professional Experience" in pattern_names:
        count += 1
        
        # Check if they have actual text to parse
        role_texts = props.get('Role', {}).get('rich_text', [])
        exp_texts = props.get('Experience_Summary', {}).get('rich_text', [])
        
        role = "".join([t.get('plain_text', '') for t in role_texts])
        exp = "".join([t.get('plain_text', '') for t in exp_texts])
        
        if not role.strip() and not exp.strip():
            empty_roles += 1

print(f"Total candidates with 'General Professional Experience': {count}")
print(f"Of those, {empty_roles} have completely empty Role/Experience fields.")
print(f"Candidates that COULD potentially be parsed if retried: {count - empty_roles}")
