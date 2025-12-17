import pymupdf
import os

# ① 처리할 PDF 파일의 경로를 문자열로 지정
pdf_file_path = "chap04/data/과정기반 작물모형을 이용한 웹 기반 밀 재배관리 의사결정 지원시스템 설계 및 구축.pdf"

# PyMuPDF(=fitz)의 고수준 API로 PDF 열기
# - 성공하면 문서 객체(doc)를 반환하며, 페이지 순회가 가능
doc = pymupdf.open(pdf_file_path)

# PDF 전체 텍스트를 누적해 담을 변수
full_text = ''

# ② 문서의 각 페이지를 순회
for page in doc:  # 문서 페이지 반복
    # 현재 페이지에서 텍스트 추출
    # - 내부적으로 레이아웃을 분석해 문자열을 반환
    text = page.get_text()
    print('='*20)
    print(text)
    print('='*20)
    # 전체 문자열에 현재 페이지 텍스트를 이어붙이기
    full_text += text

# ③ PDF 파일명만 추출(경로 제거)
pdf_file_name = os.path.basename(pdf_file_path)
# 확장자(.pdf) 제거 -> 순수 파일명만 남김
pdf_file_name = os.path.splitext(pdf_file_name)[0]

# ④ 출력할 TXT 경로 생성(ex: chap04/output/파일명.txt)
txt_file_path = f"chap04/output/{pdf_file_name}.txt"

# 텍스트 파일로 저장
# - 'w' 모드: 파일이 없으면 생성, 있으면 덮어씀
# - UTF-8 인코딩으로 저장(한글 깨짐 방지)
with open(txt_file_path, 'w', encoding='utf-8') as f:
    f.write(full_text)
