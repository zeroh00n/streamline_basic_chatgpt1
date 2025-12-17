from openai import OpenAI
from dotenv import load_dotenv
import os

# .env 파일의 환경변수를 현재 프로세스 환경으로 로드
# 예) .env 내부에 OPENAI_API_KEY=sk-... 형태로 저장되어 있어야 함
load_dotenv()
api_key = os.getenv('OPENAI_API_KEY')  # 환경변수에서 OpenAI API 키를 읽음

def summarize_txt(file_path: str): # ① 텍스트 파일 경로를 받아 요약 문자열을 반환하는 함수
    client = OpenAI(api_key=api_key)  # OpenAI 클라이언트 인스턴스 생성(키를 명시적으로 전달)

    # ② 주어진 텍스트 파일을 읽어들인다.
    # - UTF-8 인코딩으로 전체 내용을 문자열로 읽음
    # - 파일이 없으면 FileNotFoundError 발생 가능
    with open(file_path, 'r', encoding='utf-8') as f:
        txt = f.read()

    # ③ 요약을 위한 시스템 프롬프트를 생성한다.
    # - 요약 규격(제목/문제 인식 및 주장/저자 소개)을 포맷으로 안내
    # - 실제 원문 텍스트를 하단에 붙여 모델이 참고하도록 함
    # - 긴 텍스트의 경우 토큰 한도를 초과할 수 있음(모델/컨텍스트 크기 주의)
    system_prompt = f'''
    너는 다음 글을 요약하는 봇이다. 아래 글을 읽고, 저자의 문제 인식과 주장을 파악하고, 주요 내용을 요약하라. 

    작성해야 하는 포맷은 다음과 같다. 
    
    # 제목

    ## 저자의 문제 인식 및 주장 (15문장 이내)
    
    ## 저자 소개

    
    =============== 이하 텍스트 ===============

    { txt }
    '''

    # 디버깅/검증용 출력: 모델에 전달될 시스템 프롬프트 전체를 콘솔에 찍음
    # (민감정보가 포함될 수 있으니 운영환경에서는 과도한 로그 출력에 유의)
    print(system_prompt)
    print('=========================================')

    # ④ OpenAI API를 사용하여 요약을 생성한다.
    # - chat.completions.create를 사용하여 대화형 완성 호출
    # - temperature=0.1로 설정해 요약의 일관성과 결정성을 높임
    # - messages에 system 역할만 넣어도 응답이 생성되지만,
    #   일반적으로는 user/assistant 역할을 함께 쓰는 패턴이 더 흔함(여기서는 원본 유지)
    response = client.chat.completions.create(
        model="gpt-4o",      # 사용 모델 지정
        temperature=0.1,     # 무작위성(창의성) 낮춤 → 요약 결과의 안정성 강화
        messages=[
            {"role": "system", "content": system_prompt},  # 시스템 지침에 원문 포함
        ]
    )

    # 첫 번째 후보(choice)의 메시지 본문을 반환
    # - choices 배열은 n 매개변수로 여러 개 요청 시 복수 결과를 담음
    return response.choices[0].message.content

if __name__ == '__main__':
    # 요약 대상 텍스트 파일 경로 지정
    file_path = './chap04/output/과정기반 작물모형을 이용한 웹 기반 밀 재배관리 의사결정 지원시스템 설계 및 구축_with_preprocessing.txt'

    # summarize_txt 함수 호출로 요약 생성
    summary = summarize_txt(file_path)
    print(summary)  # 콘솔에 요약 출력

    # ⑤ 요약된 내용을 파일로 저장한다.
    # - 결과를 재사용/검토할 수 있도록 UTF-8로 저장
    # - 동일 경로/파일명이 존재하면 덮어씀(주의)
    with open('./chap04/output/crop_model_summary.txt', 'w', encoding='utf-8') as f:
        f.write(summary)
