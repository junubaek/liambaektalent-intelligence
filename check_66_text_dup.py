import sqlite3

def get_trigrams(text):
    if not text: return set()
    cleaned = text.replace(" ", "").replace("\n", "")
    return set([cleaned[i:i+3] for i in range(len(cleaned)-2)])

conn = sqlite3.connect('candidates.db')

missing = conn.execute("SELECT id, name_kr, raw_text FROM candidates WHERE is_duplicate=0 AND (google_drive_url IS NULL OR google_drive_url='' OR google_drive_url='#')").fetchall()
others = conn.execute("SELECT id, name_kr, raw_text FROM candidates WHERE is_duplicate=0 AND google_drive_url IS NOT NULL").fetchall()

others_processed = [(o[0], o[1], get_trigrams(o[2])) for o in others if o[2]]

print("Starting deep text similarity check...")
dups = []
for m_id, m_name, m_text in missing:
    if not m_text: continue
    m_trigrams = get_trigrams(m_text)
    if not m_trigrams: continue
    
    best_match = None
    best_score = 0
    for o_id, o_name, o_trigrams in others_processed:
        if not o_trigrams: continue
        
        intersection = m_trigrams.intersection(o_trigrams)
        union = m_trigrams.union(o_trigrams)
        if not union: continue
        
        jaccard = len(intersection) / len(union)
        if jaccard > best_score:
            best_score = jaccard
            best_match = (o_name, o_id)
            
    if best_score > 0.8: # Very high text similarity
        dups.append(f"[DB 내용 {int(best_score*100)}% 일치] {m_name} ({m_id}) == {best_match[0]} ({best_match[1]})")

print(f"Deep Text Duplicates Found: {len(dups)}\n" + "\n".join(dups))
