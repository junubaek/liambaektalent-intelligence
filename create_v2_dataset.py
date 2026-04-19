import json

DATASET_FILE = 'golden_dataset.json'
OUT_FILE = 'golden_dataset_v2.json'

mapping = {
    'Framework Software Engineer': 'vllm pytorch llm serving machine learning',
    'DevOps & Platform Engineer': 'kubernetes terraform devops aws infrastructure',
    'NPU Library Software Engineer': 'npu library c c++ cuda ai semiconductor',
    'SoC Architect for Scale-Up and Scale-Out': 'soc architecture pcie cxl scale-out',
    'Ethernet Firmware Engineer': 'ethernet firmware embedded network rtos',
    'Firmware Verification Engineer': 'firmware verification rtl uvm fpga',
    'AI Cloud Engineer': 'cloud infrastructure aws mlops kubernetes',
    'System Tools Engineer - AI Hardware': 'python c++ performance profiling ai hardware',
    'NPU Runtime Software Engineer (LLM Serving)': 'npu runtime cpp llm serving compiler',
    'Device Driver Engineer - User-Mode Driver': 'device driver linux pcie c++'
}

def create_subset():
    with open(DATASET_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    v2_data = []
    for d in data:
        q = d['jd_query']
        if q in mapping:
            # Create a copy and map
            d_new = d.copy()
            d_new['jd_query'] = mapping[q]
            v2_data.append(d_new)
            
    with open(OUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(v2_data, f, ensure_ascii=False, indent=2)
        
    print(f"Created {OUT_FILE} with {len(v2_data)} entries across {len(mapping)} targets.")

if __name__ == '__main__':
    create_subset()
