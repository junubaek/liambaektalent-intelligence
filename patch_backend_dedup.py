import codecs

def patch_backend_dedup():
    with codecs.open('jd_compiler.py', 'r', 'utf-8') as f:
        content = f.read()

    # Find the current dedup logic
    old_dedup = '''    seen_names = set()
    dedup = []
    for r in final_results:
        if '무명' in r['name_kr']:
            dedup.append(r)
            continue
            
        pure = re.sub(r'[^가-힣a-zA-Z]', '', r['name_kr'])
        if pure not in seen_names:
            seen_names.add(pure)
            dedup.append(r)
    final_results = dedup'''
    
    new_dedup = '''    # Complex Deduplication for Namesakes vs Ghosts
    grouped_by_name = {}
    for r in final_results:
        if '무명' in r['name_kr']:
            grouped_by_name.setdefault(r['id'], []).append(r)
            continue
        pure_name = re.sub(r'[^가-힣a-zA-Z]', '', r['name_kr'])
        grouped_by_name.setdefault(pure_name, []).append(r)
        
    dedup = []
    for name_key, candidates_group in grouped_by_name.items():
        if '무명' in candidates_group[0]['name_kr'] or len(candidates_group) == 1:
            dedup.append(candidates_group[0])
            continue
            
        # Group identically if they share the same phone OR exactly same current_company (and it exists)
        # Otherwise, they are treated as NAMESAKES.
        person_clusters = []
        for c in candidates_group:
            phone = c.get('phone', '').strip().replace('-', '') if c.get('phone') else ''
            company = c.get('current_company', '').strip() if c.get('current_company') else ''
            
            matched_cluster = None
            for p in person_clusters:
                p_phone = p[0].get('phone', '').strip().replace('-', '') if p[0].get('phone') else ''
                p_company = p[0].get('current_company', '').strip() if p[0].get('current_company') else ''
                
                # Loose matching: if one has same phone, OR same non-empty company
                if (phone and p_phone and phone == p_phone) or (company and p_company and company == p_company):
                    matched_cluster = p
                    break
            
            if matched_cluster: matched_cluster.append(c)
            else: person_clusters.append([c])
            
        if len(person_clusters) == 1:
            # All are the same person (ghost shells), pick the one with highest score/data
            dedup.append(person_clusters[0][0])
        else:
            # There are actual Namesakes! Append job titie to Name.
            for cluster in person_clusters:
                best_c = cluster[0] # The one with the highest score in the cluster
                job = best_c.get('seniority', '직무 미상')
                if job == 'None' or not job: job = '직무 미상'
                
                # Ensure we don't append multiple times
                if '(' not in best_c['name_kr']:
                    best_c['name_kr'] = f"{best_c['name_kr']}({job})"
                dedup.append(best_c)
                
    # Sort again because dedup might change order of clusters
    dedup.sort(key=lambda x: (x.get('_score', 0), x.get('total_edges', 0)), reverse=True)
    final_results = dedup'''
    
    if old_dedup in content:
        content = content.replace(old_dedup, new_dedup)
        with codecs.open('jd_compiler.py', 'w', 'utf-8') as f:
            f.write(content)
        print("Updated jd_compiler dedup logic successfully!")
    else:
        print("Failed to find old dedup logic.")

if __name__ == "__main__":
    patch_backend_dedup()
