import pymupdf
import os

from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv('OPENAI_API_KEY')

def summarize_txt(
        file_path: str,
        api_key: str, # 오픈AI API key
        model: str = "gpt-4o", # 오픈AI 모델
    ):
    client = OpenAI(api_key=api_key)

    # (2) 주어진 텍스트 파일을 읽어들이기
    with open(file_path, 'r', encoding='utf-8') as f:
        txt = f.read()

    # (3) 요약을 위한 시스템 프롬프트 생성하기
    system_prompt = f'''
    너는 다음 글을 요약하는 봇이다. 아래 글을 읽고, 저자의 문제 인식과 주장을 파악하고, 주요 내용을 요약하라. 

    작성해야 하는 포맷은 다음과 같다. 
    
    # 제목

    ## 저자의 문제 인식 및 주장 (15문장 이내)
    
    ## 저자 소개

    
    =============== 이하 텍스트 ===============

    { txt }
    '''

    # (4) 오픈AI API를 사용하여 요약 생성하기
    response = client.chat.completions.create(
        model=model,
        temperature=0.1,
        messages=[
            {"role": "system", "content": system_prompt},
        ]
    )

    return response.choices[0].message.content


def extract_text_from_pdf(
        pdf_file_path, 
        header_height,  # 헤더의 높이 
        footer_height,  # 푸터의 높이
    ):
        
    doc = pymupdf.open(pdf_file_path)

    full_text = ''

    for page in doc:
        rect = page.rect # 페이지 크기를 가져오기
        
        header = page.get_text(clip=(0, 0, rect.width , header_height))
        footer = page.get_text(clip=(0, rect.height - footer_height, rect.width , rect.height))
        text = page.get_text(clip=(0, header_height, rect.width , rect.height - footer_height))

        full_text += text + '\n------------------------------------\n'

    # 파일명만 추출
    pdf_file_name = os.path.basename(pdf_file_path)
    pdf_file_name = os.path.splitext(pdf_file_name)[0] # 확장자 제거

    txt_file_path = f'chap04/output/{pdf_file_name}_with_preprocessing.txt'

    with open(txt_file_path, 'w', encoding='utf-8') as f:
        f.write(full_text)

    return txt_file_path


def summarize_document(
        pdf_file_path: str,
        header_height: int,
        footer_height: int,
        api_key: str,
        model: str = "gpt-4o",
    ):    

    txt_file_path = extract_text_from_pdf(
        pdf_file_path, header_height, footer_height
    )

    print(f"Text extracted from {pdf_file_path} is saved")

    summary = summarize_txt(txt_file_path, api_key, model=model)
    print(summary)

    # (5) 요약된 내용을 파일로 저장
    summary_file_path = txt_file_path.replace('.txt', f'_summary_{model}.txt')
    with open(summary_file_path, 'w', encoding='utf-8') as f:
        f.write(summary)

    print(f"Summary is saved to {summary_file_path}")

    return summary_file_path


if __name__ == '__main__':
    pdf_file_path = "chap04/data/인격에 대한 칸트의 관점과 인공지능.pdf"
    header_height = 80
    footer_height = 80
    api_key = os.getenv('OPENAI_API_KEY')

    summary_file_path = summarize_document(
        pdf_file_path, header_height, footer_height, api_key, model="gpt-4o-mini"
    )
