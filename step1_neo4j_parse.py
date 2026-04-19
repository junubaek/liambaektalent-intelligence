import json
import os
import dynamic_parser_v2
import hashlib

print("Running dynamic_parser_v2 for 187 new resumes...")

with open(r'C:\Users\cazam\Downloads\이력서자동분석검색시스템\missing_files_report.json', 'r', encoding='utf-8') as f:
    report = json.load(f)

unmatched = report.get('unmatched_list', [])

import sqlite3
c = sqlite3.connect(r'C:\Users\cazam\Downloads\이력서자동분석검색시스템\candidates.db').cursor()
c.execute("SELECT phone FROM candidates WHERE phone IS NOT NULL AND phone != ''")
db_phones = set([row[0].replace('-', '').replace(' ', '') for row in c.fetchall()])

new_resumes = []
for u in unmatched:
    phone = u.get('extracted_phone')
    if phone and phone not in db_phones:
        new_resumes.append(u['file'])
        
print(f"Total new resume targets: {len(new_resumes)}")

files = dynamic_parser_v2.collect_files()

batch_dict = {}
for name in new_resumes:
    if name in files:
        batch_dict[name] = dynamic_parser_v2.extract_text(files[name])

print(f"Text collected for {len(batch_dict)} files.")

from tqdm import tqdm

all_names = list(batch_dict.keys())
for i in tqdm(range(0, len(all_names), 5)):
    batch_names = all_names[i:i+5]
    sub_dict = {k: batch_dict[k] for k in batch_names}
    
    parsed_results = dynamic_parser_v2.parse_resume_batch(sub_dict)
    
    for name, text in sub_dict.items():
        if name in parsed_results:
            edges = parsed_results.get(name, [])
            dynamic_parser_v2.save_edges(name, edges, text)

print("Finished parsing and saving edges to Neo4j.")
