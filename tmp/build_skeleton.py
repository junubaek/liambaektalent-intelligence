import json
import codecs
from collections import defaultdict

def extract_skills():
    try:
        with codecs.open('temp_candidates.json', 'r', encoding='utf-8-sig') as f:
            data = json.load(f)
    except Exception as e:
        print(f"Error loading temp_candidates.json: {e}")
        return

    results = data.get('results', [])
    print(f"Loaded {len(results)} candidates from temp_candidates.json")

    # Let's inspect properties of first candidate and find skill-related ones
    if not results:
        print("No candidates found.")
        return
        
    props = results[0].get('properties', {})
    skill_props = [k for k in props.keys() if 'skill' in k.lower() or 'tech' in k.lower() or '경험' in k.lower() or '경력' in k.lower() or '역량' in k.lower()]
    print(f"Potential skill properties: {skill_props}")

    # For safety, let's just dump all multi-select and select values we can find,
    # as well as specific properties if they matches known ones like 'Skills', 'Tech Stack'
    
    skill_freq = defaultdict(int)
    co_occurrences = defaultdict(lambda: defaultdict(int))
    candidate_skills_list = []

    for candidate in results:
        candidate_skills = set()
        properties = candidate.get('properties', {})
        
        for prop_name, prop_data in properties.items():
            prop_type = prop_data.get('type')
            
            # Extract skills mainly from multi_select or select
            # we will guess that if the property name has 'Skill', 'Tech', '경험' etc. it's what we want
            if any(keyword in prop_name.lower() for keyword in ['skill', 'tech', 'stack', '분야', '경험', '역량', 'sector']):
                if prop_type == 'multi_select':
                    tags = [item['name'] for item in prop_data.get('multi_select', [])]
                    for t in tags:
                        candidate_skills.add(t)
                elif prop_type == 'rich_text':
                    text_content = "".join([t.get('plain_text', '') for t in prop_data.get('rich_text', [])])
                    # simple extraction if comma separated
                    if ',' in text_content:
                        tags = [x.strip() for x in text_content.split(',')]
                        for t in tags:
                            if len(t) > 1 and len(t) < 30: # just basic filtering
                                candidate_skills.add(t)
        
        if candidate_skills:
            candidate_skills_list.append(list(candidate_skills))
            for s1 in candidate_skills:
                skill_freq[s1] += 1
                for s2 in candidate_skills:
                    if s1 != s2:
                        co_occurrences[s1][s2] += 1

    print("\n--- [항성 (Stars) - Core Skills / Experiences] ---")
    sorted_skills = sorted(skill_freq.items(), key=lambda x: x[1], reverse=True)
    
    top_stars = sorted_skills[:20]
    for skill, freq in top_stars:
        print(f"🌟 항성: [{skill}] (질량/자력: {freq})")
        
        # 궤도를 도는 인접 스킬 찾기 (Co-occurrence)
        adjacent = co_occurrences[skill]
        sorted_adjacent = sorted(adjacent.items(), key=lambda x: x[1], reverse=True)[:5]
        for adj_skill, weight in sorted_adjacent:
            print(f"    └─ 궤도 연결: {adj_skill} (Weight: {weight})")

if __name__ == '__main__':
    extract_skills()
