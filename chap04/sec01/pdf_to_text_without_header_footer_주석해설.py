import pymupdf
import os

# 처리할 PDF의 파일 경로를 지정
pdf_file_path = "chap04/data/과정기반 작물모형을 이용한 웹 기반 밀 재배관리 의사결정 지원시스템 설계 및 구축.pdf"
# PyMuPDF로 PDF 문서를 연다. 반환된 doc은 페이지를 순회(iteration)할 수 있는 객체
doc = pymupdf.open(pdf_file_path)

# 페이지 상단(헤더) 영역의 높이(px 비슷한 페이지 단위) 지정
header_height = 80
# 페이지 하단(푸터) 영역의 높이 지정
footer_height = 80

# 모든 페이지에서 추출한 본문 텍스트를 누적할 문자열 버퍼
full_text = ''

# 문서의 각 페이지를 순회
for page in doc:
    # 현재 페이지의 전체 사각영역(Rect)을 가져옴 (x0,y0,x1,y1 및 width/height 포함)
    rect = page.rect # 페이지 크기 가져오기
    
    # 헤더 부분 텍스트 추출
    # clip=(x0, y0, x1, y1) 형태로 잘라낼 사각형을 지정
    # 여기서는 좌상단(0,0)에서 페이지 폭, header_height 높이까지의 영역
    header = page.get_text(clip=(0, 0, rect.width , header_height))
    # 푸터 부분 텍스트 추출
    # 페이지 하단에서 footer_height 만큼 위로 올라온 영역부터 바닥까지
    footer = page.get_text(clip=(0, rect.height - footer_height, rect.width , rect.height))
    # 본문 텍스트 추출
    # 헤더 영역 아래부터 푸터 영역 위까지(즉, 헤더/푸터를 제외한 가운데 영역)
    text = page.get_text(clip=(0, header_height, rect.width , rect.height - footer_height))

    # 페이지별로 추출된 본문을 누적하고, 페이지 구분선(---)을 삽입
    enter_text = '\n+++++++++++++++++++++++++++++++++\n'
    full_text += text + enter_text

# 파일 경로에서 파일명만 분리(디렉터리 제거)
pdf_file_name = os.path.basename(pdf_file_path)
# 확장자(.pdf) 제거하여 순수 파일명만 얻기
pdf_file_name = os.path.splitext(pdf_file_name)[0] # 확장자 제거

# 출력 텍스트 파일 경로 생성 (전처리된 본문이므로 접미사 부여)
txt_file_path = f'chap04/output/{pdf_file_name}_with_preprocessing_2.txt'

# 텍스트 파일로 저장
# - 'w' 모드: 파일이 없으면 생성, 있으면 덮어씀
# - UTF-8로 저장해 한글 깨짐 방지
with open(txt_file_path, 'w', encoding='utf-8') as f:
    f.write(full_text)

""" 추가 팁(선택):

clip 좌표는 페이지 좌상단(0,0) 기준입니다. 헤더/푸터 높이는 PDF마다 다르니, 맞지 않으면 header_height, footer_height 값을 조정하세요.

chap04/output 폴더가 없으면 FileNotFoundError가 날 수 있으니, 필요하면 저장 전에 os.makedirs("chap04/output", exist_ok=True)를 한 줄 추가하면 안전합니다. """
