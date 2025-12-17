# ================================== 주석 해설 시작 ==================================
# 이 파일은 LangChain + OpenAI를 사용한 다중 턴 채팅 예제입니다.
# - 핵심 흐름: (1) 환경변수 로딩 -> (2) 모델/클라이언트 준비 -> (3) 메시지 히스토리 관리 -> (4) 루프에서 Human → AI 교대
# - 주의: 모든 주석은 이해를 돕기 위한 것이며, 원본 코드의 동작을 변경하지 않습니다.
# ====================================================================================

from openai import OpenAI  # 주석처리
# 환경변수(.env) 로딩: OPENAI_API_KEY 등을 현재 프로세스 환경에 주입
from dotenv import load_dotenv
import os
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage


# 환경변수(.env) 로딩: OPENAI_API_KEY 등을 현재 프로세스 환경에 주입
load_dotenv()
# 환경에서 OPENAI_API_KEY 읽기 (ChatOpenAI/SDK가 이를 사용)
api_key = os.getenv("OPENAI_API_KEY")  # 환경 변수에서 API 키 가져오기
# OpenAI 공식 SDK 클라이언트 인스턴스 생성 (직접 REST 호출 시 사용)
client = OpenAI(api_key=api_key)  # 오픈AI 클라이언트의 인스턴스 생성

# LangChain의 ChatOpenAI 모델 준비 (대화형 LLM 래퍼)
llm = ChatOpenAI(model="gpt-4o")  # ChatOpenAI 클래스의 인스턴스 생성


# def get_ai_response(messages):
#     response = client.chat.completions.create(
#         model="gpt-4o",  # 응답 생성에 사용할 모델 지정
#         temperature=0.9,  # 응답 생성에 사용할 temperature 설정
#         messages=messages,  # 대화 기록을 입력으로 전달
#     )
#     return response.choices[0].message.content  # 생성된 응답의 내용 반환

# 초기 메시지 히스토리 구성: SystemMessage로 역할 지정
messages = [
    # {"role": "system", "content": "너는 사용자를 도와주는 상담사야."},  # 초기 시스템 메시지
    SystemMessage("너는 사용자를 도와주는 상담사야."),  # 초기 시스템 메시지
]

# 메인 루프 시작: 사용자의 입력을 받아 AI 응답을 생성하는 대화 흐름
while True:
# 사용자 입력을 콘솔에서 받음 (exit 입력 시 종료)
    user_input = input("사용자: ")  # 사용자 입력 받기

# 사용자가 'exit'를 입력하면 루프 종료
    if user_input == "exit":  # ② 사용자가 대화를 종료하려는지 확인인
        break
    
    messages.append(
        # {"role": "user", "content": user_input} # 주석처리
        HumanMessage(user_input)
    )  # 사용자 메시지를 대화 기록에 추가 
    
    # ai_response = get_ai_response(messages)  # 주석처리
# 전체 히스토리(messages)를 컨텍스트로 모델에 질의하여 AI 응답 생성
    ai_response = llm.invoke(messages)  # 대화 기록을 기반으로 AI 응답 가져오기
    messages.append(
        # {"role": "assistant", "content": ai_response} # 주석처리
        ai_response
    )  # AI 응답 대화 기록에 추가하기

# 화면에 모델 응답 텍스트 출력
    print("AI: " + ai_response.content)  # AI 응답 출력