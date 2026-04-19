from pdf_to_notion import extract_text_from_doc_using_win32

file = r"C:\Users\cazam\Downloads\02_resume 전처리\JY_강산(글로벌캐스팅담당_인도네시아)부문_원본.doc"
txt = extract_text_from_doc_using_win32(file)
print("EXTRACTED:")
print(txt[:200])
