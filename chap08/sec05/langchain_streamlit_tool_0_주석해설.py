import streamlit as st

from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, ToolMessage
# ↑ LangChain에서 사용하는 메시지 타입들
#   - SystemMessage: 시스템 지시(역할/규칙 지정)
#   - HumanMessage : 사용자 프롬프트
#   - AIMessage    : 모델 응답
#   - ToolMessage  : (현재 코드에서는 사용하지 않지만) 도구 호출 결과


# openai_api_key가져오기
from openai import OpenAI  # 주석처리
# ↑ OpenAI 공식 SDK import 예시(현재는 직접 사용하지 않음)
#   - LangChain의 ChatOpenAI는 내부적으로 환경 변수(OPENAI_API_KEY)를 읽어 사용 가능

from dotenv import load_dotenv
import os
load_dotenv()  # .env 파일을 로드하여 환경 변수에 반영
api_key = os.getenv("OPENAI_API_KEY")  # 환경 변수에서 API 키 가져오기
# openai_api_key가져오기
# ※ 참고: LangChain의 ChatOpenAI는 기본적으로 환경 변수(OPENAI_API_KEY)를 사용하므로
#         아래 모델 초기화에서 따로 api_key를 넘기지 않아도 동작합니다.


# 모델 초기화
llm = ChatOpenAI(model="gpt-4o-mini")
# ↑ LangChain용 OpenAI 챗 모델 래퍼 인스턴스 생성
#   - 'gpt-4o-mini' 모델을 사용
#   - OPENAI_API_KEY는 위에서 load_dotenv()로 환경에 올라간 값을 자동 인식
# llm = ChatOpenAI(model="gpt-4o-mini", api_key=api_key)
# ↑ 필요시 명시적으로 api_key를 전달하는 대안(현재는 주석 처리)


# 사용자의 메시지 처리하기 위한 함수
def get_ai_response(messages):
    # ↑ messages: 대화 히스토리(시스템/유저/AI 메시지들의 리스트)

    response = llm.stream(messages)
    # ↑ 스트리밍 모드로 모델 호출
    #   - 토큰/청크 단위로 결과가 생성되며, 제너레이터 형태로 반환됨

    for chunk in response:
        # 생성되는 각 청크를 즉시 바깥(스트림릿 UI)으로 내보냄
        # st.chat_message(...).write_stream(...)에서 이 제너레이터를 소비하며
        # 화면에 실시간으로 출력됨
        yield chunk


# Streamlit 앱
st.title("💬 langchain_streamlit_tool_0.py")
print("")  # 콘솔에 빈 줄 출력(디버깅용, UI에는 영향 없음)
st.title("GPT-4o Langchain Chat")
# ↑ 스트림릿 앱 상단에 타이틀 2개 표시(시각적 구분용)


# 스트림릿 session_state에 메시지 저장
if "messages" not in st.session_state:
    # 최초 실행 시 대화 히스토리를 초기화
    st.session_state["messages"] = [
        SystemMessage("너는 사용자를 돕기 위해 최선을 다하는 인공지능 봇이다. "),  # 역할/규칙 정의
        AIMessage("How can I help you?")  # 초기 안내 메시지
    ]


# 스트림릿 화면에 메시지 출력
for msg in st.session_state.messages:
    # 각 메시지 객체를 타입별로 말풍선에 렌더링
    if msg.content:
        if isinstance(msg, SystemMessage):
            st.chat_message("system").write(msg.content)     # 시스템 말풍선
        elif isinstance(msg, AIMessage):
            st.chat_message("assistant").write(msg.content)  # 어시스턴트 말풍선
        elif isinstance(msg, HumanMessage):
            st.chat_message("user").write(msg.content)       # 사용자 말풍선
        # ToolMessage는 현재 히스토리에 없으므로 분기는 생략됨(위 import만 되어 있음)


# 사용자 입력 처리
if prompt := st.chat_input():
    # 사용자가 하단 입력창에 메시지를 입력하면 실행
    st.chat_message("user").write(prompt)                   # 1) 입력 즉시 사용자 말풍선 출력
    st.session_state.messages.append(HumanMessage(prompt))  # 2) 히스토리에 사용자 메시지 추가

    # 3) 현재까지의 히스토리를 기반으로 모델 스트리밍 호출
    response = get_ai_response(st.session_state["messages"])
    
    # 4) 모델의 스트리밍 응답을 실시간으로 화면에 출력
    #    write_stream()은 제너레이터를 소비하며 최종 완성된 텍스트를 문자열로 반환
    result = st.chat_message("assistant").write_stream(response)  # AI 메시지 출력

    # 5) 완성된 AI 응답 문자열을 히스토리에 저장(다음 턴 컨텍스트 유지)
    st.session_state["messages"].append(AIMessage(result))  # AI 메시지 저장
