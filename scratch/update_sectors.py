import sqlite3
import json
import sys

def main():
    sys.stdout.reconfigure(encoding='utf-8')
    conn = sqlite3.connect('candidates.db')
    cur = conn.cursor()
    
    # 1. Fetch SW and Semiconductor candidates
    cur.execute("""
        SELECT id, name_kr, profile_summary, raw_text, sector 
        FROM candidates 
        WHERE sector = 'SW' OR sector = 'Semiconductor'
    """)
    rows = cur.fetchall()
    
    # Keyword rules
    keywords_ai = ['llm', 'vllm', 'gpt', '추론', 'inference', 'mlops', 'transformer', 'fine-tuning', 'rlhf', 'model serving', 'ai 서빙', '딥러닝', 'deep learning', 'neural network', 'pytorch', 'tensorflow']
    keywords_systems = ['kernel', 'bsp', 'device driver', '디바이스 드라이버', '펌웨어', 'firmware', 'rtos', 'bootloader', '부트로더', 'linux kernel', '리눅스 커널', 'embedded', '임베디드']
    keywords_npu = ['npu', 'neural processing', '뉴럴', 'ppa', 'area optimization', 'dnn accelerator', 'chip design', '칩 설계', 'rtl', 'verilog', 'vhdl']
    keywords_soc = ['soc', 'system on chip', '시스템반도체', 'asic', 'physical design', '물리설계', 'fpga', 'tape-out', '테이프아웃', 'ip design']
    
    def check_match(text, keywords):
        if not text:
            return False
        text_lower = text.lower()
        for kw in keywords:
            if kw in text_lower:
                return True
        return False
        
    updated_counts = {
        'SW_AI': 0,
        'SW_Systems': 0,
        'Semiconductor_NPU': 0,
        'Semiconductor_SoC': 0,
        'SW': 0,
        'Semiconductor': 0
    }
    
    print("Updating sectors in SQLite DB...")
    
    updates = []
    
    for id_, name, summary, raw_text, orig_sector in rows:
        combined_text = (summary or "") + " " + (raw_text or "")
        
        if orig_sector == 'SW':
            # Priority: NPU -> SoC -> Systems -> AI
            if check_match(combined_text, keywords_npu):
                new_sector = 'Semiconductor_NPU'
            elif check_match(combined_text, keywords_soc):
                new_sector = 'Semiconductor_SoC'
            elif check_match(combined_text, keywords_systems):
                new_sector = 'SW_Systems'
            elif check_match(combined_text, keywords_ai):
                new_sector = 'SW_AI'
            else:
                new_sector = 'SW'
        elif orig_sector == 'Semiconductor':
            if check_match(combined_text, keywords_npu):
                new_sector = 'Semiconductor_NPU'
            elif check_match(combined_text, keywords_soc):
                new_sector = 'Semiconductor_SoC'
            else:
                new_sector = 'Semiconductor'
        else:
            continue
            
        updates.append((new_sector, id_))
        updated_counts[new_sector] = updated_counts.get(new_sector, 0) + 1

    # Execute updates
    cur.executemany("UPDATE candidates SET sector = ? WHERE id = ?", updates)
    conn.commit()
    conn.close()
    
    print("\n=== Sector Update Complete ===")
    print("=== New Sector Counts ===")
    for sector, cnt in sorted(updated_counts.items(), key=lambda x: -x[1]):
        print(f"  - {sector}: {cnt}명")

if __name__ == '__main__':
    main()
