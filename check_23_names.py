import sqlite3
import re

files = [
    "Heding_국문이력서 양식 (개인정보동의 포함)1_BHC_조은호.docx",
    "JY_강민아(해외매니지먼트)부문_원본.docx",
    "JY_김재원(글로벌캐스팅담당_태국)부문_원본.pdf",
    "[BX디자이너]웹디자인,UI_이은주.pdf",
    "[디셈버앤컴퍼니] 신혜수(사내변호사)부문.pdf",
    "[리벨리온] 이형무(Silicon Validation Engineer)부문.pdf",
    "[리벨리온] 최재언(Firmware Verification Engineer)부문.pdf",
    "[마이리얼트립] 신혜수(사내변호사)부문.pdf",
    "[매드업] 이희진(CTO)부문.pdf",
    "[뷰노] 신혜수(사내변호사)부문.pdf",
    "[스타비젼] 민혜식(인사팀)부문.docx",
    "[오호라(글루가)]마케팅기획부문_박지연_이력서.docx",
    "[우아한형제들] 김선덕(개인정보보호 리더급)부문.docx",
    "[챌린저스] 김율희(UX 디자이너)부문.pdf",
    "[쿠팡]UXUI디자이너_김지은.pdf",
    "[펫닥]급여,총무_박준원.docx",
    "김병구(경영기획팀 팀원)부문_원본.docx",
    "김형욱(IR 담당자)부문_원본.pdf",
    "민창근(금형설계／개발(전자／화성))부문_원본.pdf",
    "박소이(CDN 운영)부문_원본.docx",
    "박진솔(화장품 패키지디자이너)부문_원본.pdf",
    "주선유(브랜드마케터).pdf",
    "펫닥 B2B 자사몰 MD 지원_윤여주.pdf"
]

def extract_fallback_name(filename):
    m = re.search(r'[가-힣]{2,4}', filename.replace("이력서", "").replace("포트폴리오", "").replace("개발자", ""))
    return m.group(0) if m else "미상"

conn = sqlite3.connect('candidates.db')
c = conn.cursor()

found = []
missing = []

for f in files:
    name = extract_fallback_name(f)
    if name and name != "미상":
        c.execute("SELECT id, name_kr, email, current_company FROM candidates WHERE name_kr LIKE ? OR name_kr LIKE ?", (f"%{name}%", f"{name}%"))
        res = c.fetchall()
        if res:
            found.append((name, f, res))
        else:
            missing.append((name, f))

print(f"DB에 존재하는 사람: {len(found)}명")
for name, f, res in found:
    print(f"[{name}] <- '{f}'")
    for r in res:
         print(f"   ㄴ 매칭된 DB 데이터: ID={r[0]}, 이름={r[1]}, 이메일={r[2]}, 최근직장={r[3]}")

print(f"\nDB에 완전히 없는 사람 (순수 누락자): {len(missing)}명")
for name, f in missing:
    print(f"[{name}] <- '{f}'")

conn.close()
