from dynamic_parser import detect_duplicates
import hashlib

# 1. Dummy Processed Dictionary
processed = {
    "기존이력서": {
        "text_hash": hashlib.md5("original_resume_text".encode('utf-8')).hexdigest(),
        "name_kr": "김완희",
        "phone": "010-1111-2222"
    }
}

print("=== 1. Hash 중복 감지 테스트 (동일 파일) ===")
reason1, meta1 = detect_duplicates("기존이력서_복사본", "original_resume_text", processed)
print(f"Result: {reason1} (Expected: HASH_DUPE)")
print(f"Meta: {meta1}\\n")

print("=== 2. 원본과 다른 내용, 이름+연락처는 동일 (업데이트 이력서 감지 테스트) ===")
# 텍스트는 바뀌었고 전번은 유지된 파일 (파일명에서 이름 추출 테스트 포함 '김완희_최종')
reason2, meta2 = detect_duplicates("김완희_최종", "새로 갱신된 이력서 내용입니다. 010-1111-2222", processed)
print(f"Result: {reason2} (Expected: UPDATE_DUPE)")
print(f"Meta: {meta2}\\n")

print("=== 3. 아예 다른 새로운 이력서 ===")
reason3, meta3 = detect_duplicates("홍길동", "완전히 다른 내용 010-9999-9999", processed)
print(f"Result: {reason3} (Expected: OK)")
print(f"Meta: {meta3}\\n")

