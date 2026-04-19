import os
import sys

# 테스트 대상 스크립트는 dynamic_parser_v2
import dynamic_parser_v2 as v2

def test_single_resume():
    name = "법무법인한중_미국변호사_윤선아"
    print(f"[{name}] 비용 최적화 테스트 시작...")
    
    filepath = None
    for folder in [v2.FOLDER1, v2.FOLDER2, v2.FOLDER3]:
        for ext in [".pdf", ".docx", ".doc"]:
            p = os.path.join(folder, f"{name}{ext}")
            if os.path.exists(p):
                filepath = p
                break
        if filepath:
            break
            
    if not filepath:
        print("파일을 찾을 수 없습니다.")
        return
        
    text = v2.extract_text(filepath)
    if not text:
        print("텍스트 추출 실패")
        return
        
    print("\n--- V2 파싱 (스키마 강제 & 캐싱 폴백) ---")
    edges = v2.parse_resume(text)
    print(f"추출된 엣지 개수: {len(edges)}")
    for e in edges:
        print(f" - {e.action} -> {e.skill}")

if __name__ == "__main__":
    test_single_resume()
