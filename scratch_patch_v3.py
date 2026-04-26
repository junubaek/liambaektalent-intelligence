def patch_ontology():
    payload_canonical = """
# V3 기초 스택 추가
CANONICAL_MAP.update({
    "C++": "C_CPP",
    "C/C++": "C_CPP",
    "CPP": "C_CPP",
    "C언어": "C_Programming",
    "C_CPP": "C_CPP",
    "AWS": "Infrastructure_and_Cloud",
    "GCP": "Infrastructure_and_Cloud",
    "Azure": "Infrastructure_and_Cloud",
    "EC2": "Infrastructure_and_Cloud",
    "S3": "Infrastructure_and_Cloud",
    "Cloud": "Infrastructure_and_Cloud",
    "클라우드": "Infrastructure_and_Cloud",
    "MSSQL": "Database_Management",
    "MySQL": "Database_Management",
    "PostgreSQL": "Database_Management",
    "Oracle DB": "Database_Management",
    "NoSQL": "Database_Management",
    "MongoDB": "Database_Management",
    "Redis": "Database_Management",
    "Database_Management": "Database_Management",
    "ASRS": "Factory_Automation_System",
    "자동창고": "Factory_Automation_System",
    "스마트팩토리": "Manufacturing_Digital_Transformation",
    "Smart Factory": "Manufacturing_Digital_Transformation",
    "MES": "Manufacturing_Digital_Transformation",
    "WMS": "Factory_Automation_System",
    "AGV": "Robotics_and_Equipment_Control",
    "NFT": "Blockchain_Ecosystem",
    "블록체인": "Blockchain_Ecosystem",
    "Web3": "Blockchain_Ecosystem",
    "DeFi": "Blockchain_Ecosystem",
    "Smart Contract": "Blockchain_Ecosystem",
    "Solidity": "Blockchain_Ecosystem",
    "Ethereum": "Blockchain_Ecosystem",
    "Linux": "Infrastructure_and_Cloud",
    "리눅스": "Infrastructure_and_Cloud",
    "Ubuntu": "Infrastructure_and_Cloud",
    "CentOS": "Infrastructure_and_Cloud",
    "RDMA": "High_Performance_Computing",
    "RoCE": "High_Performance_Computing",
    "InfiniBand": "InfiniBand_Network",
    "NVLink": "High_Performance_Computing",
    "Fintech": "FinTech",
    "핀테크": "FinTech",
    "PG": "Payment_and_Settlement_System",
    "결제": "Payment_and_Settlement_System",
    "Spring": "Backend_Java",
    "Spring Boot": "Backend_Java",
    "SpringBoot": "Backend_Java",
    "JPA": "Backend_Java",
    "Hibernate": "Backend_Java",
    "MyBatis": "Backend_Java",
    "Parallel Programming": "High_Performance_Computing",
    "병렬 프로그래밍": "High_Performance_Computing",
    "Neural Network": "Deep_Learning",
    "뉴럴네트워크": "Deep_Learning"
})
"""
    
    payload_gravity = """
# V3 누락 노드 추가
UNIFIED_GRAVITY_FIELD.update({
    "C_CPP": {
        "core_attracts": {
            "Embedded_Linux":0.8,
            "Sys_Software":0.8,
            "High_Performance_Computing":0.7,
            "Firmware":0.7
        },
        "repels": {
            "Brand_Management":-0.5,
            "Content_Marketing":-0.5,
            "Tax_Accounting":-0.5,
            "HR_Strategic_Planning":-0.4
        }
    },
    "Database_Management": {
        "core_attracts": {
            "Backend_Engineering":0.8,
            "Data_Engineering":0.7,
            "Backend_Architecture":0.7
        },
        "repels": {
            "Brand_Management":-0.4,
            "Content_Marketing":-0.4,
            "Tax_Accounting":-0.4
        }
    },
    "Blockchain_Ecosystem": {
        "core_attracts": {
            "FinTech":0.7,
            "Backend_Engineering":0.6,
            "New_Business_Development":0.5
        },
        "repels": {
            "Brand_Management":-0.3,
            "Tax_Accounting":-0.4,
            "HR_Strategic_Planning":-0.4,
            "Financial_Accounting":-0.3
        }
    },
    "Manufacturing_Digital_Transformation": {
        "core_attracts": {
            "Factory_Automation_System":0.9,
            "Factory_and_Logistics_Automation":0.8,
            "Process_Engineering":0.7
        },
        "repels": {
            "Brand_Management":-0.5,
            "Frontend_Development":-0.4,
            "Content_Marketing":-0.5,
            "Tax_Accounting":-0.5
        }
    },
    "Factory_Automation_System": {
        "core_attracts": {
            "Manufacturing_Digital_Transformation":0.9,
            "Robotics_and_Equipment_Control":0.8,
            "Factory_and_Logistics_Automation":0.8
        },
        "repels": {
            "Brand_Management":-0.5,
            "Frontend_Development":-0.4,
            "Content_Marketing":-0.5,
            "Tax_Accounting":-0.5,
            "Backend_Engineering":-0.2
        }
    },
    "Robotics_and_Equipment_Control": {
        "core_attracts": {
            "Factory_Automation_System":0.9,
            "Robotics":0.9,
            "Embedded_Linux":0.6
        },
        "repels": {
            "Brand_Management":-0.5,
            "Content_Marketing":-0.5,
            "Tax_Accounting":-0.5,
            "Financial_Accounting":-0.5
        }
    },
    "FinTech": {
        "core_attracts": {
            "Payment_and_Settlement_System":0.8,
            "Backend_Engineering":0.7,
            "Financial_Accounting":0.5
        },
        "repels": {
            "Brand_Management":-0.3,
            "Content_Marketing":-0.3,
            "HR_Strategic_Planning":-0.3
        }
    },
    "Backend_Java": {
        "core_attracts": {
            "Backend_Engineering":0.9,
            "Backend_Architecture":0.8,
            "MSA_Architecture":0.7
        },
        "repels": {
            "Brand_Management":-0.5,
            "Content_Marketing":-0.5,
            "Tax_Accounting":-0.5,
            "HR_Strategic_Planning":-0.4
        }
    },
    "High_Performance_Computing": {
        "core_attracts": {
            "GPGPU":0.9,
            "AI_Model_and_Distributed_Training":0.8,
            "Infrastructure_and_Cloud":0.7,
            "Sys_Software":0.7
        },
        "repels": {
            "Brand_Management":-0.5,
            "Frontend_Development":-0.4,
            "Tax_Accounting":-0.5,
            "Content_Marketing":-0.5,
            "Financial_Accounting":-0.5
        }
    }
})
"""
    with open('ontology_graph.py', 'a', encoding='utf-8') as f:
        f.write(payload_canonical)
        f.write(payload_gravity)

if __name__ == '__main__':
    patch_ontology()
    print("Patched ontology_graph.py successfully!")
