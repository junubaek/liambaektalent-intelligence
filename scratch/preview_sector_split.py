import sqlite3
import re
import sys

def main():
    sys.stdout.reconfigure(encoding='utf-8')
    conn = sqlite3.connect('candidates.db')
    cur = conn.cursor()
    
    # 1. Fetch SW candidates
    cur.execute("""
        SELECT id, name_kr, profile_summary, raw_text, sector 
        FROM candidates 
        WHERE sector = 'SW'
    """)
    rows = cur.fetchall()
    
    # 2. Keywords compilation
    # SW_AI: LLM, vLLM, GPT, 추론, inference, MLOps, Transformer, fine-tuning, RLHF, model serving, AI 서빙, 딥러닝, deep learning, neural network, PyTorch, TensorFlow
    keywords_ai = [
        'llm', 'vllm', 'gpt', '추론', 'inference', 'mlops', 'transformer', 
        'fine-tuning', 'rlhf', 'model serving', 'ai 서빙', '딥러닝', 
        'deep learning', 'neural network', 'pytorch', 'tensorflow'
    ]
    
    # SW_Systems: kernel, BSP, device driver, 디바이스 드라이버, 펌웨어, firmware, RTOS, bootloader, 부트로더, Linux kernel, 리눅스 커널, embedded, 임베디드
    keywords_systems = [
        'kernel', 'bsp', 'device driver', '디바이스 드라이버', '펌웨어', 'firmware', 
        'rtos', 'bootloader', '부트로더', 'linux kernel', '리눅스 커널', 'embedded', '임베디드'
    ]
    
    # Semiconductor_NPU: NPU, neural processing, 뉴럴, PPA, area optimization, DNN accelerator, chip design, 칩 설계, RTL, Verilog, VHDL
    keywords_npu = [
        'npu', 'neural processing', '뉴럴', 'ppa', 'area optimization', 'dnn accelerator', 
        'chip design', '칩 설계', 'rtl', 'verilog', 'vhdl'
    ]
    
    # Semiconductor_SoC: SoC, System on Chip, 시스템반도체, ASIC, physical design, 물리설계, FPGA, tape-out, 테이프아웃, IP design
    keywords_soc = [
        'soc', 'system on chip', '시스템반도체', 'asic', 'physical design', '물리설계', 
        'fpga', 'tape-out', '테이프아웃', 'ip design'
    ]
    
    classification_results = {
        'SW_AI': [],
        'SW_Systems': [],
        'Semiconductor_NPU': [],
        'Semiconductor_SoC': [],
        'Unclassified_SW': []
    }
    
    def check_match(text, keywords):
        if not text:
            return False
        text_lower = text.lower()
        for kw in keywords:
            # Simple substring matching for robustness in multi-language resume search
            if kw in text_lower:
                return True
        return False

    for id_, name, summary, raw_text, orig_sector in rows:
        combined_text = (summary or "") + " " + (raw_text or "")
        
        matched_categories = []
        if check_match(combined_text, keywords_ai):
            matched_categories.append('SW_AI')
        if check_match(combined_text, keywords_systems):
            matched_categories.append('SW_Systems')
        if check_match(combined_text, keywords_npu):
            matched_categories.append('Semiconductor_NPU')
        if check_match(combined_text, keywords_soc):
            matched_categories.append('Semiconductor_SoC')
            
        if not matched_categories:
            classification_results['Unclassified_SW'].append((id_, name))
        else:
            # If multiple matching categories, assign to the first matched one or prioritize
            # Let's prioritize NPU/SoC first, then Systems, then AI to avoid standard SW bloat
            if 'Semiconductor_NPU' in matched_categories:
                chosen = 'Semiconductor_NPU'
            elif 'Semiconductor_SoC' in matched_categories:
                chosen = 'Semiconductor_SoC'
            elif 'SW_Systems' in matched_categories:
                chosen = 'SW_Systems'
            else:
                chosen = 'SW_AI'
            classification_results[chosen].append((id_, name))
            
    print("=== SW 서브섹터 세분화 모의 결과 ===")
    total = 0
    for category, items in classification_results.items():
        print(f"📁 {category}: {len(items)}명")
        total += len(items)
    print(f"총 검토 SW 후보자: {total}명")
    
    print("\n=== 카테고리별 샘플 (최대 10명) ===")
    for category, items in classification_results.items():
        samples = [name for _, name in items[:10]]
        print(f"* {category} 샘플: {samples}")
        
    conn.close()

if __name__ == '__main__':
    main()
