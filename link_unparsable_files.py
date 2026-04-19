import os
import sqlite3
import re
import json
from googleapiclient.http import MediaFileUpload
from connectors.gdrive_api import GDriveConnector

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

TARGET_DIRS = [
    r"C:\Users\cazam\Downloads\02_resume 전처리",
    r"C:\Users\cazam\Downloads\02_resume_converted_v8"
]

def find_file(filename):
    for d in TARGET_DIRS:
        fp = os.path.join(d, filename)
        if os.path.exists(fp):
            return fp
    return None

def main():
    print("Google Drive API Authenticating...")
    
    gdrive = GDriveConnector()
    with open(r"C:\Users\cazam\Downloads\이력서자동분석검색시스템\secrets.json", 'r') as f:
        folder_id = json.load(f)["GOOGLE_DRIVE_FOLDER_ID"]
    
    conn = sqlite3.connect('candidates.db')
    c = conn.cursor()
    
    exact_names = {
        "Heding_국문이력서 양식 (개인정보동의 포함)1_BHC_조은호.docx": "조은호",
        "JY_강민아(해외매니지먼트)부문_원본.docx": "강민아",
        "JY_김재원(글로벌캐스팅담당_태국)부문_원본.pdf": "김재원",
        "[BX디자이너]웹디자인,UI_이은주.pdf": "이은주",
        "[디셈버앤컴퍼니] 신혜수(사내변호사)부문.pdf": "신혜수",
        "[리벨리온] 이형무(Silicon Validation Engineer)부문.pdf": "이형무",
        "[리벨리온] 최재언(Firmware Verification Engineer)부문.pdf": "최재언",
        "[마이리얼트립] 신혜수(사내변호사)부문.pdf": "신혜수",
        "[매드업] 이희진(CTO)부문.pdf": "이희진",
        "[뷰노] 신혜수(사내변호사)부문.pdf": "신혜수",
        "[스타비젼] 민혜식(인사팀)부문.docx": "민혜식",
        "[오호라(글루가)]마케팅기획부문_박지연_이력서.docx": "박지연",
        "[우아한형제들] 김선덕(개인정보보호 리더급)부문.docx": "김선덕",
        "[챌린저스] 김율희(UX 디자이너)부문.pdf": "김율희",
        "[쿠팡]UXUI디자이너_김지은.pdf": "김지은",
        "[펫닥]급여,총무_박준원.docx": "박준원",
        "김병구(경영기획팀 팀원)부문_원본.docx": "김병구",
        "김형욱(IR 담당자)부문_원본.pdf": "김형욱",
        "민창근(금형설계／개발(전자／화성))부문_원본.pdf": "민창근",
        "박소이(CDN 운영)부문_원본.docx": "박소이",
        "박진솔(화장품 패키지디자이너)부문_원본.pdf": "박진솔",
        "주선유(브랜드마케터).pdf": "주선유",
        "펫닥 B2B 자사몰 MD 지원_윤여주.pdf": "윤여주"
    }
    
    success = 0
    for filename, name in exact_names.items():
        fp = find_file(filename)
        if not fp:
            print(f"File not found on disk: {filename}")
            continue
            
        print(f"Processing {name} -> {filename}")
        
        c.execute("SELECT id, google_drive_url FROM candidates WHERE name_kr LIKE ?", (f"%{name}%",))
        matches = c.fetchall()
        
        if not matches:
            print(f"   [!] Candidate {name} not found in DB.")
            continue
            
        ext = filename.lower().split('.')[-1]
        mt = 'application/pdf' if ext == 'pdf' else 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        
        try:
            drive_res = gdrive.service.files().list(q=f"name='{filename}' and '{folder_id}' in parents and trashed=false", fields="files(id, webViewLink)").execute()
            if drive_res.get('files'):
                drive_link = drive_res['files'][0]['webViewLink']
            else:
                media = MediaFileUpload(fp, mimetype=mt, resumable=True)
                uploaded = gdrive.service.files().create(body={'name': filename, 'parents': [folder_id]}, media_body=media, fields='webViewLink').execute()
                drive_link = uploaded.get('webViewLink')
        except Exception as e:
            print(f"   [!] Drive Upload Error: {e}")
            continue
            
        for m in matches:
            cid, existing_url = m
            if not existing_url:
                c.execute("UPDATE candidates SET google_drive_url = ? WHERE id = ?", (drive_link, cid))
                conn.commit()
                print(f"   [OK] Linked to DB ID {cid}")
                success += 1
            else:
                print(f"   [SKIP] Already has URL: {existing_url}")
                
    print(f"\nDone! Linked {success} missing URLs.")

if __name__ == "__main__":
    main()
