# ================================== 주석 해설 시작 ==================================
# 이 파일은 OpenAI GPT(멀티모달)와 이미지(base64) 입력을 활용해
# 이미지 기반 객관식 퀴즈를 생성하고, 결과를 마크다운/JSON 파일로 저장하는 예제입니다.
# - 핵심 흐름: (1) .env 로딩 → (2) OpenAI 클라이언트 준비 → (3) 이미지 base64 인코딩
#             (4) chat.completions에 이미지+텍스트 프롬프트 전달 → (5) 응답 파싱/저장
# - 주의: 아래 주석은 이해를 돕는 설명이며 **원본 코드 동작은 변경하지 않습니다.**
# ====================================================================================

# glob: 특정 패턴에 매칭되는 파일 경로(예: *.jpg)를 리스트업
from glob import glob # 추후 for문으로 여러 파일의 경로를 가져오기 위해 선언
# OpenAI: Chat Completions(멀티모달) 호출을 위한 공식 SDK
from openai import OpenAI
# .env의 OPENAI_API_KEY 등을 읽어 환경변수에 주입하기 위한 유틸
from dotenv import load_dotenv
import os
import base64

# .env 파일 로딩 실행 – os.getenv(...)로 키를 읽을 수 있게 함
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")  # 환경 변수에서 API 키 가져오기
# OpenAI 클라이언트 인스턴스 생성 (api_key 인자 사용 또는 환경변수 자동 사용)
client = OpenAI(api_key=api_key)  # OpenAI 클라이언트의 인스턴스 생성

# 이미지 파일을 이진으로 읽어 **base64 문자열**로 인코딩하여 반환
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")
    

# 주요 로직: 한 장의 이미지를 입력으로 받아 **퀴즈 텍스트**를 생성
# - 프롬프트(문항 양식/예시)를 텍스트로, 이미지를 data URL(base64)로 함께 전달
# - 응답에서 모델의 message.content를 그대로 반환(또는 재시도 로직 포함)
# 재시도 로직: 실패 시 일정 횟수까지 재귀적으로 재호출
def image_quiz(image_path, n_trial=0, max_trial=3):
# 재시도 로직: 실패 시 일정 횟수까지 재귀적으로 재호출
    if n_trial >= max_trial: # 최대 시도 회수에 도달하면 포기
        raise Exception("Failed to generate a quiz.")
    
    base64_image = encode_image(image_path) # 이미지를 base64로 인코딩

# 프롬프트 텍스트: 문항 형식/조건(정답은 1~4 중 하나) 등을 명시
    quiz_prompt = """
    제공된 이미지를 바탕으로, 다음과 같은 양식으로 퀴즈를 만들어주세요. 
    정답은 1~4 중 하나만 해당하도록 출제하세요.
    토익 리스닝 문제 스타일로 문제를 만들어주세요.
    아래는 예시입니다. 
    ----- 예시 -----

    Q: 다음 이미지에 대한 설명 중 옳지 않은 것은 무엇인가요?
    - (1) 베이커리에서 사람들이 빵을 사고 있는 모습이 담겨 있습니다.
    - (2) 맨 앞에 서 있는 사람은 빨간색 셔츠를 입고 있습니다.
    - (3) 기차를 타기 위해 줄을 서 있는 사람들이 있습니다.
    - (4) 점원은 노란색 티셔츠를 입고 있습니다.

# 토익 리스닝 스타일 섹션 존재 여부로 정답 형식 충족 검사
    Listening: Which of the following descriptions of the image is incorrect?
    - (1) It shows people buying bread at a bakery.
    - (2) The person standing at the front is wearing a red shirt.
    - (3) There are people lining up to take a train.
    - (4) The clerk is wearing a yellow T-shirt.
        
    정답: (4) 점원은 노란색 티셔츠가 아닌 파란색 티셔츠를 입고 있습니다.
    (주의: 정답은 1~4 중 하나만 선택되도록 출제하세요.)
    ======
    """

    messages = [
        {
            "role": "user",
            "content": [
                {"type": "text", "text": quiz_prompt},
                {
# 멀티모달 입력: 이미지(base64) data URL을 message에 첨부
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{base64_image}",
                    },
                },
            ],
        }
    ]

    try: 
# Chat Completions API 호출 – 모델/메시지(텍스트+이미지)를 전달하여 응답 생성
        response = client.chat.completions.create(
            model="gpt-4o",  # 응답 생성에 사용할 모델 지정
            messages=messages # 대화 기록을 입력으로 전달
        )
    except Exception as e:
        print("failed\n" + e)
# 재시도 로직: 실패 시 일정 횟수까지 재귀적으로 재호출
        return image_quiz(image_path, n_trial+1)
    
# 첫 번째 후보(choice)의 message.content(텍스트)를 결과로 사용
    content = response.choices[0].message.content

# 토익 리스닝 스타일 섹션 존재 여부로 정답 형식 충족 검사
    if "Listening:" in content:
        return content, True
    else:
# 재시도 로직: 실패 시 일정 횟수까지 재귀적으로 재호출
        return image_quiz(image_path, n_trial+1)


q = image_quiz("./chap06/data/images/busan_dive.jpg")
print(q)



txt = '' # ①  문제들을 계속 붙여 나가기 위해 빈 문자열 선언
no = 1 # 문제 번호를 위해 선언
# 배치 처리: 특정 폴더의 모든 JPG 이미지에 대해 반복적으로 문제 생성
for g in glob('./chap06/data/images/*.jpg'):  # ②
    q, is_suceed = image_quiz(g)

    if not is_suceed:
        continue


    divider = f'## 문제 {no}\n\n'
    print(divider)
    
    txt += divider  # ③
    # 파일명 추출해 이미지 링크 만들기
# 이미지 파일 이름만 추출해 마크다운 이미지 링크(상대 경로)로 삽입
    filename = os.path.basename(g) # ③ 마크다운에 표시할 이미지 파일 경로 설정   
    txt += f'![image]({filename})\n\n' # ③

    # 문제 추가
    print(q)
    txt += q + '\n\n---------------------\n\n'
    # ④ 마크다운 파일로 저장
# 마크다운 파일로 누적 저장: 각 문항을 구분선과 함께 기록
    with open('./chap06/sec02/sec02data/images/image_quiz_eng.md', 'w', encoding='utf-8') as f:
        f.write(txt)
    
    no += 1 # 문제 번호 증가

