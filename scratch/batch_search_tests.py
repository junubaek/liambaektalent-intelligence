import sys
import sqlite3
import os

# Set encoding for output
sys.stdout.reconfigure(encoding='utf-8')

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import api_search_v9
from jd_compiler import api_search_v9

queries = [
    # Semiconductor/HW
    'RTL Design Verilog SoC IP',
    'Physical Design Place Route Timing',
    'DFT SCAN ATPG Semiconductor',
    'HBM Memory Architecture Design',
    'Firmware Driver Embedded Linux ARM',
    'Chip Bring-up Validation Board',
    'NPU AI Accelerator Architecture',
    # AI/ML
    'LLM Inference Optimization CUDA TensorRT',
    'Deep Learning Computer Vision PyTorch',
    'MLOps Kubernetes Pipeline Infrastructure',
    'Collective Communication RDMA InfiniBand',
    # SW
    'Kubernetes DevOps Terraform Cloud',
    'Backend Spring Java Microservice',
    'Linux Kernel System Programming',
    # Finance/Business
    'Treasury Cash Flow Financial Management',
    'IPO Valuation Financial Modeling',
    'B2B Sales Enterprise Partnership',
    'SCM Supply Chain Procurement Global',
]

print("Starting batch search tests...")

for q in queries:
    try:
        r = api_search_v9(q)
        matched = r.get('matched', [])
        print(f'\n[{q}]')
        if not matched:
            print("  (No results found)")
        for i, c in enumerate(matched[:3]):
            name = c.get('name_kr', 'Unknown')
            company = c.get('current_company', 'Unknown')
            cid = str(c.get('id', ''))[:8]
            print(f'  {i+1}. {name} | {company} | {cid}')
    except Exception as e:
        print(f'\n[{q}] Error: {str(e)}')
