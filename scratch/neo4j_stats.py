from neo4j import GraphDatabase
import json
import sys

def main():
    sys.stdout.reconfigure(encoding='utf-8')
    secrets = json.load(open('secrets.json', encoding='utf-8'))
    driver = GraphDatabase.driver(secrets['NEO4J_URI'], auth=(secrets['NEO4J_USERNAME'], secrets['NEO4J_PASSWORD']))

    with driver.session() as s:
        print('=== Neo4j AI/반도체/시스템 핵심 노드 & 엣지 현황 ===')
        
        # 1. Total nodes per label
        labels = s.run('CALL db.labels() YIELD label RETURN label').value()
        for label in sorted(labels):
            cnt = s.run(f'MATCH (n:{label}) RETURN count(n) as c').single()['c']
            print(f'  - 노드 라벨 [{label}]: {cnt}개')
            
        # 2. Key standardized skill node counts for AI/Semiconductor/Systems
        target_skills = [
            'GPGPU', 'LLM_Inference', 'Model_Parallelism', 'vLLM', 'MLOps', 'PyTorch', 
            'TensorFlow', 'Transformer', 'RLHF', 'GPU_Driver', 'MoE', 'PD_Disaggregation',
            'DeepSeek-R1', 'LLM_Serving', 'Sys_Software', 'Firmware', 'Embedded_Systems',
            'ARM_Architecture', 'Linux_Kernel', 'RTOS', 'Device_Driver', 'BSP', 'Bootloader',
            'PCIe_Protocol', 'NPU_Design', 'RTL_Design', 'Verilog', 'VHDL', 'DNN_Accelerator',
            'SoC', 'PPA_Optimization', 'Chip_Design', 'Memory_Architecture', 'ASIC', 'FPGA',
            'Physical_Design', 'Tape_Out', 'IP_Design'
        ]
        
        print('\n=== 핵심 표준 스킬 노드 연결 엣지 수 (Top 20) ===')
        skill_counts = []
        for skill in target_skills:
            res = s.run('MATCH (s:Skill {name: $name})<-[r]-() RETURN count(r) as c', name=skill).single()
            if res:
                skill_counts.append((skill, res['c']))
                
        for skill, cnt in sorted(skill_counts, key=lambda x: -x[1])[:20]:
            print(f'  - 스킬 [{skill}]: 연결 엣지 수 {cnt}개')

    driver.close()

if __name__ == '__main__':
    main()
