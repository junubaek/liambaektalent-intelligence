import sys
import os

# dynamic_parser.py 경로 추가
sys.path.append(r"C:\Users\cazam\Downloads\이력서자동분석검색시스템")

from dynamic_parser import extract_text, parse_resume, save_edges

FOLDER1 = r"C:\Users\cazam\Downloads\02_resume 전처리"
FOLDER2 = r"C:\Users\cazam\Downloads\02_resume_converted_docx"

# C그룹 후보자 3명
group_c_names = [
    "법무법인한중_미국변호사_윤선아",
    "JYP_미국변호사_박다희",
    "법률사무소그루_변호사_박세진"
]

def find_filepath(name):
    # Try FOLDER1
    for ext in [".pdf", ".docx", ".doc"]:
        p = os.path.join(FOLDER1, name + ext)
        if os.path.exists(p):
            return p
            
    # Try FOLDER2
    for ext in [".pdf", ".docx", ".doc"]:
        p = os.path.join(FOLDER2, name + ext)
        if os.path.exists(p):
            return p
            
    return None

def reparse_candidates():
    for name in group_c_names:
        print(f"\n[{name}] 파일 경로 탐색...")
        filepath = find_filepath(name)
        if not filepath:
            print(f"-> 에러: {name} 파일을 찾을 수 없습니다.")
            continue
            
        print(f"-> 파일 발견: {filepath}")
        text = extract_text(filepath)
        if len(text) < 100:
            print("-> 에러: 텍스트가 100자 미만입니다.")
            continue
            
        print("-> LLM 파싱 시작...")
        edges = parse_resume(text)
        
        if edges:
            print(f"-> 파싱 성공! 추출된 엣지 수: {len(edges)}")
            for edge in edges:
                print(f"   - {edge}")
            print("-> Neo4j 적재 (및 필요시 큐 저장) 진행 중...")
            save_edges(name, edges, filepath)
        else:
            print("-> 여전히 빈 배열([])이 반환되었습니다.")

    print("\n작업이 모두 완료되었습니다.")

if __name__ == "__main__":
    reparse_candidates()
