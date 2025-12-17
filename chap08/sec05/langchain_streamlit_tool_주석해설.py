import streamlit as st
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, ToolMessage

from langchain_core.tools import tool
from datetime import datetime
import pytz

# openai_api_key가져오기
from openai import OpenAI  # 주석처리
from dotenv import load_dotenv
import os
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")  # 환경 변수에서 API 키 가져오기
# openai_api_key가져오기

# 모델 초기화
# - LangChain용 OpenAI 챗 모델 래퍼
# - 여기서는 경량 멀티모달 계열 'gpt-4o-mini'를 사용
llm = ChatOpenAI(model="gpt-4o-mini")

# 도구 함수 정의
@tool
def get_current_time(timezone: str, location: str) -> str:
    """현재 시각을 반환하는 함수."""
    # - LangChain의 @tool 데코레이터로 도구(툴)로 노출
    # - LLM이 함수 호출(툴 콜)을 결정하면, 이 함수가 실행됨
    try:
        # 입력받은 타임존 문자열을 pytz 객체로 변환
        tz = pytz.timezone(timezone)
        # 해당 타임존의 현재 시각을 'YYYY-MM-DD HH:MM:SS' 문자열로 포맷
        now = datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")
        # 사람이 읽기 좋은 결과 문자열 구성
        result = f'{timezone} ({location}) 현재시각 {now}'
        print(result)  # 서버 로그에 출력(디버깅/모니터링 용)
        return result   # LangChain이 ToolMessage로 감쌀 수 있는 문자열 반환
    except pytz.UnknownTimeZoneError:
        # 유효하지 않은 타임존일 때 예외 처리
        return f"알 수 없는 타임존: {timezone}"

# 도구 바인딩
tools = [get_current_time]                  # 사용할 도구 목록
tool_dict = {"get_current_time": get_current_time}  # 이름→실제 함수 매핑 딕셔너리

# LLM에 도구 사용 능력 바인딩
# - 이 객체로 stream()/invoke() 등을 호출하면 모델이 필요시 tool_calls를 생성
llm_with_tools = llm.bind_tools(tools)


# 사용자의 메시지 처리하기 위한 함수
def get_ai_response(messages):
    # ① 도구가 바인딩된 LLM으로 스트리밍 호출
    # - messages: System/Human/AI/Tool 메시지의 리스트(대화 히스토리)
    # - stream()은 토큰/청크 단위로 생성 결과를 순차 반환하는 제너레이터
    response = llm_with_tools.stream(messages) # ① llm.stream()을 llm_with_tools.stream()로 변경
    
    gathered = None # ② 전체 스트림을 누적하여 최종 청크(메타 포함)를 보관할 변수
    for chunk in response:
        # 스트리밍 UI를 위해 생성되는 각 청크를 즉시 밖으로 전달(yield)
        yield chunk
        
        if gathered is None: #  ③ 첫 번째 청크면 누적 시작
            gathered = chunk
        else:
            # 이후 청크들은 += 로 병합( LangChain 메시지 청크 객체 병합 연산 지원 가정 )
            gathered += chunk
 
    # 스트리밍이 끝난 시점에서, 모델이 툴 호출을 요청했는지 확인
    if gathered.tool_calls:
        # 방금까지의 모델 출력(툴 콜 메타 포함)을 대화 히스토리에 추가
        st.session_state.messages.append(gathered)
        
        # tool_calls에 포함된 각 툴 호출을 실제로 실행
        for tool_call in gathered.tool_calls:
            # 모델이 지정한 name을 키로 실제 파이썬 함수 선택
            selected_tool = tool_dict[tool_call['name']]
            # LangChain Tool.invoke(...)로 호출 인자 전달 및 실행
            # - tool_call 안에 name/args/id 등의 정보가 들어있다고 가정
            tool_msg = selected_tool.invoke(tool_call) 
            print(tool_msg, type(tool_msg))  # 디버깅 출력
            # 툴 실행 결과를 ToolMessage로 세션 히스토리에 추가(스트림릿 표시용)
            st.session_state.messages.append(tool_msg)
           
        # 툴 실행 결과까지 히스토리에 반영했으니,
        # 다음 턴(후속 응답)을 얻기 위해 재귀적으로 다시 LLM 호출 (ReAct 루프 패턴)
        for chunk in get_ai_response(st.session_state.messages):
            yield chunk


# Streamlit 앱
st.title("💬 GPT-4o Langchain Chat")  # 앱 타이틀

# 스트림릿 session_state에 메시지 저장
# - 첫 방문 시 초기 시스템 프롬프트와 간단한 AI 인사말을 세팅
if "messages" not in st.session_state:
    st.session_state["messages"] = [
        SystemMessage("너는 사용자를 돕기 위해 최선을 다하는 인공지능 봇이다. "),  # 역할 규정
        AIMessage("How can I help you?")  # 첫 안내 메시지
    ]

# 스트림릿 화면에 메시지 출력
# - 세션에 쌓인 대화(시스/유저/AI/툴)를 각각 다른 말풍선으로 표시
for msg in st.session_state.messages:
    if msg.content:
        if isinstance(msg, SystemMessage):
            st.chat_message("system").write(msg.content)
        elif isinstance(msg, AIMessage):
            st.chat_message("assistant").write(msg.content)
        elif isinstance(msg, HumanMessage):
            st.chat_message("user").write(msg.content)
        elif isinstance(msg, ToolMessage):
            st.chat_message("tool").write(msg.content)


# 사용자 입력 처리
# - 하단 입력창에서 프롬프트가 들어오면 즉시 한 턴 대화를 진행
if prompt := st.chat_input():
    st.chat_message("user").write(prompt)                      # 사용자 메시지 화면 출력
    st.session_state.messages.append(HumanMessage(prompt))     # 사용자 메시지 히스토리 저장

    # LLM 스트리밍 응답 제너레이터 획득
    response = get_ai_response(st.session_state["messages"])
    
    # 스트리밍된 청크를 말풍선에 실시간으로 표출
    # - write_stream은 제너레이터를 받아 순차적으로 출력하고, 최종 텍스트를 반환
    result = st.chat_message("assistant").write_stream(response) # AI 메시지 출력
    # 최종 결과 텍스트를 AIMessage로 히스토리에 저장(다음 턴 문맥 유지)
    st.session_state["messages"].append(AIMessage(result)) # AI 메시지 저장


""" 
동작 흐름 핵심 요약

세션 초기화: SystemMessage로 역할을 정하고, 간단 인사 AIMessage를 초기 히스토리에 추가합니다.

입력 → 스트리밍 응답: 사용자가 입력하면 get_ai_response()로 LLM을 스트리밍 호출하여 토큰 단위로 화면에 출력합니다.

툴 호출(옵션): 모델이 tool_calls를 생성한 경우, 해당 도구(여기서는 get_current_time)를 실제로 실행하고, 도구 결과를 히스토리에 추가한 뒤 재귀 호출로 후속 답변을 이어갑니다(일종의 ReAct 패턴).

히스토리 관리: 모든 턴의 System/Human/AI/Tool 메시지를 st.session_state["messages"]에 쌓아 대화 맥락 유지를 보장합니다.

실무 팁(선택)

환경변수 로딩: .env에 OPENAI_API_KEY를 넣고 load_dotenv()로 로딩했으니, Streamlit 실행 전 환경이 올바른지 확인하세요.

툴 인자 구조: tool_call의 구조는 LangChain/SDK 버전에 따라 {"name": ..., "args": {...}} 혹은 ToolCall 객체일 수 있습니다. 현재 코드는 selected_tool.invoke(tool_call)을 가정하므로, 버전에 따라 selected_tool.invoke(tool_call["args"])가 필요할 수 있습니다. (여기서는 로직 변경 없이 주석으로만 안내)

타임존 문자열: 예) "Asia/Seoul", "America/New_York"처럼 IANA 타임존을 사용해야 합니다. 잘못된 문자열이면 "알 수 없는 타임존" 메시지가 반환됩니다.

스트리밍 예외 처리: 네트워크/쿼터 에러 시 UI가 멈출 수 있으니, 실무에서는 try/except로 get_ai_response() 내부를 감싸고 오류 메시지를 st.error()로 보여주면 UX가 좋아집니다.

필요하면 툴 호출 인자 구조에 맞춰 한 줄만 바꾸는 버전도 만들어 드릴게요. """





