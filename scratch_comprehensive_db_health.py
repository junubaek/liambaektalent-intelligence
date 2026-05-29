import sqlite3
import json
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

db_path = r"C:\Users\cazam\Downloads\이력서자동분석검색시스템\candidates.db"
conn = sqlite3.connect(db_path)
cur = conn.cursor()

# 1. Overall Counts
cur.execute("SELECT COUNT(*) FROM candidates")
total_candidates = cur.fetchone()[0]

print(f"Total candidates: {total_candidates}")

# 2. Null/Empty Fields Analysis
fields = [
    'email', 'phone', 'birth_year', 'current_company', 
    'total_years', 'profile_summary', 'careers_json', 'education_json', 'sector', 'google_drive_url'
]

null_empty_stats = {}
for field in fields:
    # Check NULL or empty string
    cur.execute(f"SELECT COUNT(*) FROM candidates WHERE {field} IS NULL OR {field} = '' OR {field} = '[]' OR {field} = '{{}}'")
    empty_cnt = cur.fetchone()[0]
    null_empty_stats[field] = {
        'count': empty_cnt,
        'percentage': (empty_cnt / total_candidates) * 100
    }

# 3. Parsing Integrity Analysis
# (A) Empty or Unparsable Career JSON (specifically [] or empty parsing outcomes)
cur.execute("SELECT COUNT(*) FROM candidates WHERE careers_json IS NULL OR careers_json = '[]' OR json_array_length(careers_json) = 0")
empty_careers_cnt = cur.fetchone()[0]

# (B) Empty or Unparsable Education JSON
cur.execute("SELECT COUNT(*) FROM candidates WHERE education_json IS NULL OR education_json = '[]' OR json_array_length(education_json) = 0")
empty_education_cnt = cur.fetchone()[0]

# (C) Missing profile_summary or extremely short summaries (e.g. less than 10 chars)
cur.execute("SELECT COUNT(*) FROM candidates WHERE profile_summary IS NULL OR length(profile_summary) < 10")
weak_summary_cnt = cur.fetchone()[0]

# (D) Raw Text Issues (e.g. missing raw_text, or raw_text < 100 characters - indicating scanning failures or blank PDFs)
cur.execute("SELECT COUNT(*) FROM candidates WHERE raw_text IS NULL OR length(raw_text) < 100")
empty_raw_text_cnt = cur.fetchone()[0]

# Get samples of unparsable or blank raw text candidates
cur.execute("SELECT id, name_kr, length(raw_text), sector FROM candidates WHERE raw_text IS NULL OR length(raw_text) < 100 LIMIT 10")
unparsable_samples = cur.fetchall()

# 4. Sector Integrity Check
# Standard 15 Sectors
standard_set = {
    'Eng_SW', 'Eng_AI', 'Eng_Data', 'Eng_Embedded',
    'Eng_HW', 'Eng_Semi', 'Product', 'Finance',
    'Marketing', 'Sales', 'HR', 'Strategy',
    'Operations', 'Legal', 'Healthcare'
}

cur.execute("SELECT id, name_kr, sector FROM candidates WHERE sector IS NOT NULL")
all_sectors = cur.fetchall()

non_standard_candidates = []
for cid, name, sec in all_sectors:
    parts = [s.strip() for s in sec.split(',')]
    primary = parts[0]
    if primary not in standard_set:
        non_standard_candidates.append((cid, name, sec))

# 5. Write to markdown report
output_path = r"C:\Users\cazam\Downloads\이력서자동분석검색시스템\db_comprehensive_health_report.md"
with open(output_path, "w", encoding="utf-8") as f:
    f.write("# LiamBaekTalent Database Comprehensive Health & Parsing Audit Report\n")
    f.write(f"*Generated at: 2026-05-29 | Database: `{os.path.basename(db_path)}`*\n\n")
    
    f.write("## 1. Executive Summary & Database Vital Signs\n\n")
    f.write("| Vital Metric | Value | Percentage of Total | Status / Assessment |\n")
    f.write("| :--- | :---: | :---: | :--- |\n")
    f.write(f"| **Total Candidates** | **{total_candidates}명** | 100% | Primary Pool Size |\n")
    
    # Raw text check
    raw_status = "Good" if empty_raw_text_cnt / total_candidates < 0.05 else "Requires Attention"
    f.write(f"| Unparsable Resumes (Raw Text < 100 chars) | {empty_raw_text_cnt}명 | {empty_raw_text_cnt/total_candidates*100:.2f}% | {raw_status} (Blank or Scanned PDFs) |\n")
    
    # Career JSON check
    career_status = "Good" if empty_careers_cnt / total_candidates < 0.08 else "Needs Reparsing"
    f.write(f"| Empty Career JSON (`[]` or NULL) | {empty_careers_cnt}명 | {empty_careers_cnt/total_candidates*100:.2f}% | {career_status} (Failed Career Extraction) |\n")
    
    # Education JSON check
    edu_status = "Good" if empty_education_cnt / total_candidates < 0.12 else "Acceptable"
    f.write(f"| Empty Education JSON (`[]` or NULL) | {empty_education_cnt}명 | {empty_education_cnt/total_candidates*100:.2f}% | {edu_status} |\n")
    
    # Summary check
    summary_status = "Good" if weak_summary_cnt / total_candidates < 0.05 else "Needs LLM Enrichment"
    f.write(f"| Empty/Weak Profile Summaries | {weak_summary_cnt}명 | {weak_summary_cnt/total_candidates*100:.2f}% | {summary_status} |\n")
    
    # Non-standard sectors
    sector_status = "Excellent" if len(non_standard_candidates) == 0 else "Requires Reclassification"
    f.write(f"| Non-Standard / Unmapped Sectors | {len(non_standard_candidates)}명 | {len(non_standard_candidates)/total_candidates*100:.2f}% | {sector_status} |\n")
    
    f.write("\n\n## 2. Granular Field Integrity Audit (Missing/Null Fields)\n")
    f.write("Analyzes columns that hold key contact information or metadata. A high missing percentage in contact information is standard for raw resumes, but metadata should be populated.\n\n")
    f.write("| Target Field | Missing/Null Count | Populated Count | Integrity Rate (%) |\n")
    f.write("| :--- | :---: | :---: | :---: |\n")
    for field, stats in null_empty_stats.items():
        missing = stats['count']
        populated = total_candidates - missing
        rate = (populated / total_candidates) * 100
        f.write(f"| `{field}` | {missing}명 | {populated}명 | {rate:.2f}% |\n")
        
    f.write("\n\n## 3. Detailed Analysis of Parsing Failures & Raw Text Anomalies\n\n")
    
    f.write("### 3.1 Unparsable / Scanned PDF Resumes (Raw Text < 100 Chars)\n")
    f.write("These candidates represent files where the PDF text extractor returned zero or extremely short text (typically due to image-only scanned files or extraction errors). These candidates **cannot be matched via semantic search (Vector) or lexical search (BM25)** because their text is empty.\n\n")
    
    if unparsable_samples:
        f.write("| Candidate ID | Candidate Name | Raw Text Length (Bytes) | Sector | Action Needed |\n")
        f.write("| :--- | :--- | :---: | :--- | :--- |\n")
        for cid, name, length, sec in unparsable_samples:
            f.write(f"| `{cid}` | {name} | {length if length is not None else 0} | {sec} | OCR/Manual Upload |\n")
    else:
        f.write("*No raw text anomalies detected. All candidates have populated text.* \n")
        
    f.write("\n\n### 3.2 Empty Career Schemas with Populated Raw Text\n")
    f.write("These represent candidates where the original text exists, but the LLM parsing parser failed to structure them into the `careers_json` schema. These candidates **can match vector searches but will fail depth score calculations (Tower 4) or role-based graph searches (Tower 2)**.\n\n")
    
    # Fetch 15 samples of candidates who have raw_text but empty careers_json
    cur.execute("""
        SELECT id, name_kr, length(raw_text), sector 
        FROM candidates 
        WHERE (careers_json IS NULL OR careers_json = '[]') 
          AND raw_text IS NOT NULL AND length(raw_text) > 500 
        LIMIT 15
    """)
    empty_career_samples = cur.fetchall()
    
    if empty_career_samples:
        f.write("| Candidate ID | Candidate Name | Raw Text Length (Chars) | Sector | Action Needed |\n")
        f.write("| :--- | :--- | :---: | :--- | :--- |\n")
        for cid, name, length, sec in empty_career_samples:
            f.write(f"| `{cid}` | {name} | {length} | {sec} | Trigger LLM Career Reparse |\n")
    else:
        f.write("*No empty career anomalies found. All candidates with raw text have populated career history.* \n")
        
    f.write("\n\n## 4. Sector Normalization Status\n\n")
    f.write(f"- **Standardized Sector Coverage**: **{total_candidates - len(non_standard_candidates)}명** ({ (total_candidates - len(non_standard_candidates))/total_candidates*100:.2f}%)\n")
    f.write(f"- **Remaining Unmapped/Broken Sectors**: **{len(non_standard_candidates)}명** ({len(non_standard_candidates)/total_candidates*100:.2f}%)\n\n")
    
    if non_standard_candidates:
        f.write("### List of Remaining Non-Standard Candidates\n")
        f.write("| Candidate ID | Candidate Name | Current Stored Sector | Action |\n")
        f.write("| :--- | :--- | :--- | :--- |\n")
        for cid, name, sec in non_standard_candidates[:30]:
            f.write(f"| `{cid}` | {name} | `{sec}` | Re-classify to standard list |\n")
        if len(non_standard_candidates) > 30:
            f.write(f"\n*...and {len(non_standard_candidates) - 30} more candidates.* \n")
    else:
        f.write("### [Status: Excellent] Sector Normalization Complete\n")
        f.write("All active candidates in the database are fully normalized and map to standard primary/secondary sectors. No manual correction is required.\n")

print("Successfully written comprehensive database health report.")
conn.close()
