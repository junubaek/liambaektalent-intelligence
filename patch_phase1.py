updates = [
    # AI/LLM
    ('vLLM', 'vLLM'),
    ('SGLang', 'SGLang'),
    ('KV Caching', 'KV_Caching'),
    ('KV-cache', 'KV_Caching'),
    ('PD disaggregation', 'PD_Disaggregation'),
    ('CUDA', 'CUDA'),
    ('HIP', 'HIP'),
    ('Triton', 'Triton'),
    ('PyTorch', 'PyTorch'),
    ('TensorFlow', 'TensorFlow'),
    ('JAX', 'JAX'),
    ('TensorRT', 'TensorRT'),
    ('TensorRT-LLM', 'TensorRT_LLM'),
    ('NCCL', 'NCCL'),
    ('RCCL', 'RCCL'),
    ('DeepEP', 'DeepEP'),
    ('MoE', 'MoE'),
    ('Tensor Parallel', 'Tensor_Parallel'),
    ('Expert Parallel', 'Expert_Parallel'),
    # 네트워킹/인터커넥트
    ('RDMA', 'RDMA'),
    ('RoCE', 'RoCE'),
    ('RoCEv2', 'RoCEv2'),
    ('InfiniBand', 'InfiniBand'),
    ('EFA', 'EFA'),
    ('Ethernet', 'Ethernet'),
    ('PCIe', 'PCIe'),
    ('NVMe', 'NVMe'),
    ('NVMe-oF', 'NVMe_oF'),
    ('CXL', 'CXL'),
    ('PCIe Gen5', 'PCIe_Gen5'),
    ('ARM', 'ARM_Architecture'),
    ('RISC-V', 'RISC_V'),
    # 재무/회계
    ('연결회계', 'Consolidated_Accounting'),
    ('연결재무제표', 'Consolidated_Accounting'),
    ('자회사 회계', 'Consolidated_Accounting'),
    ('K-IFRS', 'K_IFRS'),
    ('US GAAP', 'US_GAAP'),
    ('K-GAAP', 'K_GAAP'),
    ('IFRS', 'IFRS'),
    ('재무회계', 'Financial_Accounting'),
    ('Financial Accounting', 'Financial_Accounting'),
    ('Accounting', 'Financial_Accounting'),
    ('회계감사', 'Financial_Audit'),
    ('외부감사', 'Financial_Audit'),
    ('내부회계관리제도', 'Internal_Control'),
    ('내부통제', 'Internal_Control'),
    ('Internal Control', 'Internal_Control'),
    ('FP&A', 'FP_and_A'),
    ('Strategic Finance', 'FP_and_A'),
    ('재무기획', 'FP_and_A'),
    ('경영기획', 'Corporate_Planning'),
    ('사업계획', 'Corporate_Planning'),
    ('Corporate Planning', 'Corporate_Planning'),
    ('Financial Systems', 'Financial_Systems_Management'),
    ('ERP 구현', 'Financial_Systems_Management'),
    ('Financial System Manager', 'Financial_Systems_Management'),
    ('CPA', 'CPA'),
    ('AICPA', 'AICPA'),
    ('CFA', 'CFA'),
    ('재경관리사', 'Financial_Certificate_KR'),
    ('Forensic Accounting', 'Forensic_Accounting'),
    ('포렌식 회계', 'Forensic_Accounting'),
    ('Due Diligence', 'Due_Diligence'),
    ('CDD', 'Due_Diligence'),
    ('M&A 실사', 'Due_Diligence'),
    ('Valuation', 'Valuation'),
    ('기업가치평가', 'Valuation'),
    # 에너지/전력
    ('전력계통', 'Power_Grid_Engineering'),
    ('계통연계', 'Power_Grid_Engineering'),
    ('Power System', 'Power_Grid_Engineering'),
    ('Grid', 'Power_Grid_Engineering'),
    ('BESS', 'BESS'),
    ('ESS', 'ESS'),
    ('태양광', 'Solar_Energy'),
    ('VPP', 'VPP'),
    ('재생에너지', 'Renewable_Energy'),
    ('Renewable Energy', 'Renewable_Energy'),
    # 반도체 설계
    ('Physical Design', 'Physical_Design'),
    ('Place and Route', 'Physical_Design'),
    ('Backend Design', 'Physical_Design'),
    ('DFT', 'DFT'),
    ('Design for Testability', 'DFT'),
    ('RTL Design', 'RTL_Design'),
    ('RTL', 'RTL_Design'),
    ('SoC Design', 'SoC_Design'),
    ('IP Design', 'IP_Design'),
    ('Verification', 'Hardware_Verification'),
    ('UVM', 'UVM'),
    ('SystemVerilog', 'SystemVerilog'),
    ('Verilog', 'Verilog'),
    ('Silicon Validation', 'Silicon_Validation'),
    ('Post-Silicon', 'Silicon_Validation'),
    ('Chip Bring-up', 'Chip_Bringup'),
    ('Board Bring-up', 'Board_Bringup'),
    ('SerDes', 'SerDes'),
    ('HBM', 'HBM'),
    ('HBM3', 'HBM3'),
    ('TSV', 'TSV'),
    ('2.5D', 'Advanced_Packaging'),
    ('3DIC', 'Advanced_Packaging'),
    # CCL/분산통신
    ('Collective Communication', 'Collective_Communication'),
    ('CCL', 'Collective_Communication'),
    ('MPI', 'MPI'),
    ('OpenMPI', 'OpenMPI'),
    ('AllReduce', 'AllReduce'),
    ('Ring AllReduce', 'AllReduce'),
    # DevOps/인프라
    ('Kubernetes', 'Kubernetes'),
    ('k8s', 'Kubernetes'),
    ('Terraform', 'Terraform'),
    ('Helm', 'Helm'),
    ('ArgoCD', 'ArgoCD'),
    ('GitOps', 'GitOps'),
    ('LangGraph', 'LangGraph'),
    ('LangChain', 'LangChain'),
    ('MLOps', 'MLOps'),
    ('Kubeflow', 'Kubeflow'),
    ('Karpenter', 'Karpenter'),
    ('Istio', 'Istio'),
    ('Prometheus', 'Prometheus'),
    ('Grafana', 'Grafana'),
    ('Datadog', 'Datadog'),
    # PR/커뮤니케이션
    ('PR', 'Public_Relations'),
    ('홍보', 'Public_Relations'),
    ('Public Relations', 'Public_Relations'),
    ('언론홍보', 'Public_Relations'),
    ('IR', 'Investor_Relations'),
    ('투자자관계', 'Investor_Relations'),
    # 음악/저작권
    ('음악 저작권', 'Music_Rights'),
    ('Music Rights', 'Music_Rights'),
    ('저작권', 'Copyright_Management'),
    ('콘텐츠 저작권', 'Copyright_Management'),
    # 기술영업/FDE
    ('Forward Deployed', 'Forward_Deployed_Engineering'),
    ('FDE', 'Forward_Deployed_Engineering'),
    ('Solutions Engineer', 'Solutions_Engineering'),
    ('Pre-Sales Engineer', 'Solutions_Engineering')
]

def patch_ontology():
    lines = open('ontology_graph.py', 'r', encoding='utf-8').readlines()
    
    update_keys = {u[0] for u in updates}
    
    new_lines = []
    in_canonical = False
    brace_found = False
    
    for i, line in enumerate(lines):
        # Determine if we are inside CANONICAL_MAP
        if "CANONICAL_MAP: dict[str, str] =" in line:
            in_canonical = True
            
        if in_canonical:
            # Check for keys to delete
            stripped = line.strip()
            # It looks like "vLLM": "LLM_Serving" or 'vLLM': "..."
            skip = False
            for k in update_keys:
                if stripped.startswith(f'"{k}":') or stripped.startswith(f"'{k}':"):
                    skip = True
                    break
            if skip:
                continue
                
            if line.strip() == "}":
                # We reached the end of CANONICAL_MAP!
                # Inject new updates
                new_lines.append("    # === Phase 1 Raw Node Deep Patches ===\n")
                for k, v in updates:
                    new_lines.append(f'    "{k}": "{v}",\n')
                new_lines.append("}\n")
                in_canonical = False
                brace_found = True
                continue
                
        new_lines.append(line)
        
    with open('ontology_graph.py', 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
    print("Patched ontology_graph.py successfully!")

if __name__ == '__main__':
    patch_ontology()
