
import json
import os
from connectors.openai_api import OpenAIClient
from jd_analyzer_v5 import JDAnalyzerV5

def test_analysis():
    secrets_path = "secrets.json"
    with open(secrets_path, "r") as f:
        secrets = json.load(f)
    
    openai = OpenAIClient(secrets["OPENAI_API_KEY"])
    analyzer = JDAnalyzerV5(openai)
    
    jd_text = """
Position: Data Analyst
합류하게 될 팀에 대해 알려드려요

Data Analyst(Strategy) 포지션은 Strategy Team에 속해 있어요.
Strategy Team은 전사의 주요 경영 지표(KPI) 설계 및 성과 트래킹, 사업 계획수립을 담당하며, 데이터에 기반해 회사의 중·장기 사업 방향과 실행 전략을 점검하고 개선하는 역할을 합니다.
분석 결과를 만드는 팀이 아니라 ‘회사가 지금 무엇에 집중해야 하는지’를 정의하는 팀입니다.
합류하면 함께할 업무예요

전사의 data_driven 문화를 이끌어가며, 더 나은 의사결정을 위한 인사이트를 제공합니다.
비즈니스의 핵심 KPI를 정의하고 성과를 구조적으로 트레킹 합니다.
(문제 정의 → 가설 수립 → 분석/모델링 → 임팩트 추정 → 실행안 도출 → 실행결과 회고 및 Next Action) 전 과정에 주도적으로 참여합니다.
고객 상담 및 설계사의 리텐션·생산성, Sales 상품, 판매수수료 체계 등 핵심 비즈니스 데이터를 분석해 성과 차이의 원인을 파악하고, 개선 전략을 도출합니다.
다양한 조직과 협업하며 신규 기회 영역을 발굴하는 Data Coordinator 역할을 수행합니다.
분석결과를 시각화하고, 이해관계자를 설득하는 커뮤니케이션을 담당합니다.
이런 분과 함께하고 싶어요

논리적 사고와 문제 해결력을 바탕으로 데이터를 활용하여 인사이트를 도출하고, 구성원을 설득하여 비즈니스 성과로 연결해 본 경험이 있으신 분
도메인 지식에 대한 호기심이 많고, 데이터 분석을 통해 깊이 있는 인사이트를 찾고자 하는 분
SQL을 통해 원하는 데이터를 직접 추출하고 정제할 수 있는 분
Tableau 등 데이터 시각화 도구를 활용해 데이터를 효과적으로 전달할 수 있는 분
"""
    
    print("Analyzing JD...")
    result = analyzer.analyze(jd_text)
    print(json.dumps(result, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    test_analysis()
