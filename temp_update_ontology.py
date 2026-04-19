import os

ROOT_DIR = r"c:\Users\cazam\Downloads\이력서자동분석검색시스템"
file_path = os.path.join(ROOT_DIR, "ontology_graph.py")

with open(file_path, "r", encoding="utf-8") as f:
    lines = f.readlines()

mappings = {
    "RTL 설계": "RTL_Design",
    "ASIC RTL 설계": "RTL_Design",
    "FPGA RTL 설계": "RTL_Design",
    "DFE SoC RTL 설계": "RTL_Design",
    "SoC RTL 설계": "RTL_Design",
    "RTL 개발": "RTL_Design",
    "RTL 품질": "RTL_Design",
    "회로설계": "Circuit_Design",
    "회로 설계 이론": "Circuit_Design",
    "OLED TV 주변 회로": "Circuit_Design",
    "Isolation/Non-isolation 회로": "Circuit_Design",
    "WiFi 회로": "Circuit_Design",
    "analog/digital 회로": "Circuit_Design",
    "고속 디지털 시스템 설계": "Circuit_Design",
    "CD DRIVE MODULE HW설계": "Circuit_Design",
    "IP 설계 규격": "Circuit_Design",
    "mask설계": "Semiconductor_Process",
    "LAY-OUT 설계": "Circuit_Design",
    "태양전지 공정": "Semiconductor_Process",
    "CMP 공정": "Semiconductor_Process",
    "MEMS 공정": "Semiconductor_Process",
    "EPI - FAB 공정": "Semiconductor_Process",
    "FAB LC 공정 기술": "Semiconductor_Process",
    "FAB 공정 장비 개발": "Semiconductor_Process",
    "FAB 공정장비": "Semiconductor_Process",
    "Laser 공정": "Semiconductor_Process",
    "Laser 공정 기술": "Semiconductor_Process",
    "Laser 공정 품질": "Semiconductor_Process",
    "Laser Marking 공정": "Semiconductor_Process",
    "Lamination 공정": "Semiconductor_Process",
    "SAW 공정": "Semiconductor_Process",
    "Mold 공정": "Semiconductor_Process",
    "DES공정": "Semiconductor_Process",
    "OTP 공정 Flow": "Semiconductor_Process",
    "AMOLED FAB Laminator 공정장비": "Semiconductor_Process",
    "ceramic wafer 공정": "Semiconductor_Process",
    "photo litho 공정 setup": "Semiconductor_Process",
    "Reflector lift-off 공정 개발": "Semiconductor_Process",
    "회로 형성 공정": "Semiconductor_Process",
    "Ag Wire Bonding공정": "Semiconductor_Process",
    "Die/Wire Bonding공정": "Semiconductor_Process",
    "Direct Bonding 공정 운영": "Semiconductor_Process",
    "SMT 공정품질": "Semiconductor_Process",
    "IMT 공정품질": "Semiconductor_Process",
    "CNC 공정 기술": "Semiconductor_Process",
    "CNC 공정 제조": "Semiconductor_Process",
    "CNC 공정 품질": "Semiconductor_Process",
    "Module 공정 장비 개발": "Semiconductor_Process",
    "Module 공정장비": "Semiconductor_Process",
    "OCA 기구조립 공정 Set-Up": "Semiconductor_Process",
    "OCA 기구조립 공정 운영": "Semiconductor_Process",
    "OCR 기구조립 공정 Set-Up": "Semiconductor_Process",
    "OCR 기구조립 공정 운영": "Semiconductor_Process",
    "Laser Cutting 자동화 장비 설계": "Semiconductor_Process",
    "Laser Cutting자동화 장비 설계": "Semiconductor_Process",
    "Chip 검증": "Chip_Verification",
    "PoC 검증": "Chip_Verification",
    "제어 시스템 검증": "Chip_Verification",
    "BIW 강성 목표치 검증": "Chip_Verification",
    "제품 안정성 검증": "Quality_Management",
    "Kafka 테스트 및 검증": "QA_and_Testing",
    "블랙박스 테스트": "QA_and_Testing",
    "회귀 테스트": "QA_and_Testing",
    "테스트 자동화": "QA_and_Testing",
    "테스트 결과 분석": "QA_and_Testing",
    "테스트 리포팅": "QA_and_Testing",
    "테스트 프로세스": "QA_and_Testing",
    "API 테스트 커버리지": "QA_and_Testing",
    "HA 테스트": "QA_and_Testing",
    "FluentD 테스트": "QA_and_Testing",
    "3G 모바일 테스트 시스템": "QA_and_Testing",
    "Rest 서비스 테스트": "QA_and_Testing",
    "운영 및 테스트": "QA_and_Testing",
    "품질 및 신뢰성 테스트": "Quality_Management",
    "임베디드 시스템": "Embedded_System",
    "Micom 펌웨어": "Firmware_Development",
    "FW_컨트롤러": "Firmware_Development",
    "기계 설계": "Mechanical_Design",
    "기계설계": "Mechanical_Design",
    "금형 설계": "Mechanical_Design",
    "프레스 금형 설계": "Mechanical_Design",
    "JIG 설계": "Mechanical_Design",
    "HEAT PIPE 설계": "Mechanical_Design",
    "냉각용 HEAT SINK 설계": "Mechanical_Design",
    "3D 설계": "Mechanical_Design",
    "3D 설계(Sketchup)": "Mechanical_Design",
    "2D 설계": "Mechanical_Design",
    "공압 Line 설계": "Mechanical_Design",
    "진공 공압 Line 설계": "Mechanical_Design",
    "자동화 Line 설계": "Mechanical_Design",
    "자동화 시스템 설계": "Industrial_Automation",
    "자동화 설계": "Industrial_Automation",
    "제어 전장 설계": "Industrial_Automation",
    "제어설계": "Industrial_Automation",
    "Cutting Table 설계": "Mechanical_Design",
    "DASH ASSY 설계": "Mechanical_Design",
    "자동차 설계": "Automotive_Engineering",
    "Line 설계": "Industrial_Automation",
    "Line증설계획": "Industrial_Automation",
    "공정 Set-up": "Manufacturing_Process",
    "공정 개선 Spec": "Manufacturing_Process",
    "공정 관리": "Manufacturing_Process",
    "공정 설계": "Manufacturing_Process",
    "공정 장비 Set Up": "Manufacturing_Process",
    "공정 조건 설정": "Manufacturing_Process",
    "공정 합리화": "Manufacturing_Process",
    "공정 Management": "Manufacturing_Process",
    "신규 열융착 공정 Set up": "Manufacturing_Process",
    "FPM 사업 공정 설계": "Manufacturing_Process",
    "FPM 사업 공정 셋업": "Manufacturing_Process",
    "FPM 사업 공정 운영": "Manufacturing_Process",
    "시스템 설계": "System_Architecture",
    "네트워크 설계": "Network_Engineering",
    "통신 시스템 설계": "Network_Engineering",
    "API 설계": "API_Development",
    "DB 설계": "Database_Design",
    "DB설계": "Database_Design",
    "DB 구조 재설계": "Database_Design",
    "RDB모델링/설계": "Database_Design",
    "DW 설계": "Data_Warehouse",
    "IT 설계": "System_Architecture",
    "ERP 구성항목 설계": "ERP",
    "시스템 자동화 설계": "System_Architecture",
    "프로세스 설계": "Business_Process_Management",
    "로그 설계": "System_Architecture",
    "UI/UX 설계": "UX_UI_Design",
    "User Flow 설계": "UX_UI_Design",
    "사용성 테스트": "UX_UI_Design",
    "사용자 조사 설계": "UX_Research",
    "A/B 테스트": "AB_Testing",
    "AB test 설계": "AB_Testing",
    "AB 테스트": "AB_Testing",
    "설문 설계": "UX_Research",
    "비즈니스 모델 설계": "Business_Model_Development",
    "시장성 테스트": "Market_Research",
    "원가설계": "Cost_Management",
    "실험설계": "Research_and_Development",
    "설계 및 시공 관리": "Construction_Management",
    "실시설계": "Construction_Management",
    "시설 설계": "Construction_Management",
    "공간 설계": "Construction_Management",
    "인테리어 설계": "Construction_Management",
    "매장 설계": "Construction_Management",
    "모델하우스 설계": "Construction_Management",
    "국제 규격 설계 검토": "Quality_Management",
    "결제 서비스 재설계": "FinTech",
    "구독 서비스 정책 설계": "Product_Planning",
    "임상시험 및 피부 자극 테스트": "Cosmetics_and_Beauty",
    "반도체 MES": "Semiconductor_Process",
    "제품 설계": "Product_Development",
    "설계 Surface 기술": "Mechanical_Design",
    "검사구 설계": "Quality_Management",
    "FLOOR 설계": "Construction_Management"
}

end_idx = -1
in_canonical = False
for i, line in enumerate(lines):
    if line.startswith("CANONICAL_MAP:") or line.startswith("CANONICAL_MAP ="):
        in_canonical = True
    elif in_canonical and line.strip() == "}":
        # First closing bracket after CANONICAL_MAP declaration
        end_idx = i
        break

if end_idx != -1:
    lines[end_idx-1] = lines[end_idx-1].rstrip('\n')
    if not lines[end_idx-1].endswith(','):
        lines[end_idx-1] += ',\n'
    else:
        lines[end_idx-1] += '\n'
        
    insert_lines = []
    insert_lines.append("\n    # HW/Semiconductor Long-tail Phase 3 Merge\n")
    for k, v in mappings.items():
        if v == "SKIP": continue
        insert_lines.append(f'    "{k}": "{v}",\n')
        
    lines = lines[:end_idx] + insert_lines + lines[end_idx:]
    
    with open(file_path, "w", encoding="utf-8") as f:
        f.writelines(lines)
    print("CANONICAL_MAP successfully expanded!")
else:
    print("Failed to find CANONICAL_MAP in ontology_graph.py")
