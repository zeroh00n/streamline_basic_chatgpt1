import streamlit as st

from langchain_openai import ChatOpenAI  # 오픈AI 모델을 사용하는 랭체인 챗봇 클래스
from langchain_core.chat_history import InMemoryChatMessageHistory  # 메모리에 대화 기록을 저장하는 클래스
from langchain_core.runnables.history import RunnableWithMessageHistory  # 메시지 기록을 활용해 실행 가능한 wrapper 클래스
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage  # 메시지 타입 정의(사람/AI/시스템)

# openai_api_key가져오기
from openai import OpenAI  # 주석처리
from dotenv import load_dotenv
import os
load_dotenv()  # .env 파일의 환경변수를 현재 프로세스 환경변수로 로드
api_key = os.getenv("OPENAI_API_KEY")  # 환경 변수에서 API 키 가져오기 (ChatOpenAI는 기본적으로 이를 자동 사용)
# openai_api_key가져오기


# --- Streamlit UI 헤더 ---
st.title("💬 Chatbot")  # 앱 제목 표시

# --- Streamlit 세션 상태에 대화 메시지 히스토리 초기화 ---
if "messages" not in st.session_state:
    # 최초 실행 시 SystemMessage로 역할/톤 지정(사용자에게 직접 전송되지는 않지만 화면엔 표시됨)
    st.session_state["messages"] = [
        SystemMessage("너는 사용자의 질문에 친절이 답하는 AI챗봇이다.")
    ]

# --- 세션별 대화 기록 저장소 초기화 ---
# RunnableWithMessageHistory가 사용할 히스토리 저장소(store)를 session_state에 둠(서버 재실행 간 유지)
if "store" not in st.session_state:
    st.session_state["store"] = {}

def get_session_history(session_id: str):
    """
    RunnableWithMessageHistory가 요구하는 형태의 '히스토리 로더' 콜백.
    - session_id별로 InMemoryChatMessageHistory 인스턴스를 생성/반환한다.
    - InMemoryChatMessageHistory는 LangChain 포맷의 메시지를 보관/조회하는 경량 저장소이다.
    """
    if session_id not in st.session_state["store"]:
        st.session_state["store"][session_id] = InMemoryChatMessageHistory()
    return st.session_state["store"][session_id]

# --- LLM(언어모델) 준비 및 히스토리 래핑 ---
llm = ChatOpenAI(model="gpt-4o-mini")  # OPENAI_API_KEY를 환경변수에서 읽어 모델 초기화
# RunnableWithMessageHistory: LLM 호출 시 자동으로 세션별 히스토리를 가져와 문맥에 포함시켜 준다.
with_message_history = RunnableWithMessageHistory(llm, get_session_history)

# --- Runnable 실행시 사용할 구성값 ---
# configurable.session_id에 의해 get_session_history(session_id)로 해당 세션 히스토리를 로드한다.
config = {"configurable": {"session_id": "abc2"}}

# --- 기존 히스토리를 UI에 렌더링 ---
for msg in st.session_state.messages:
    if msg:  # None 방지
        if isinstance(msg, SystemMessage):
            st.chat_message("system").write(msg.content)     # 시스템 메시지를 'system' 말풍선으로
        elif isinstance(msg, AIMessage):
            st.chat_message("assistant").write(msg.content)  # AI 응답을 'assistant' 말풍선으로
        elif isinstance(msg, HumanMessage):
            st.chat_message("user").write(msg.content)       # 사용자 메시지를 'user' 말풍선으로

# --- 사용자 입력 처리 ---
if prompt := st.chat_input():
    print('user:', prompt)  # 콘솔 로그(디버깅용)
    # 1) 대화 히스토리에 HumanMessage 추가(다음 턴 문맥 유지)
    st.session_state.messages.append(HumanMessage(prompt))
    # 2) UI에 사용자 메시지 표시
    st.chat_message("user").write(prompt)

    # 3) RunnableWithMessageHistory로 스트리밍 호출
    #    - 내부적으로 config의 session_id를 통해 get_session_history를 호출하여
    #      InMemoryChatMessageHistory를 불러오고, 거기에 메시지를 축적한다.
    #    - 여기서는 모델 입력으로 [HumanMessage(prompt)]만 넘기지만,
    #      RunnableWithMessageHistory가 과거 히스토리를 합쳐 컨텍스트를 구성한다.
    response = with_message_history.stream([HumanMessage(prompt)], config=config)

    # 4) 스트리밍된 청크를 누적하면서 화면에 실시간 표시
    ai_response_bucket = None  # 누적 버퍼(청크 결합용). LangChain의 메시지 청크가 가정됨.
    # st.chat_message("assistant").empty(): 어시스턴트 말풍선 컨테이너를 만들고 비워둔 상태로 사용
    with st.chat_message("assistant").empty():
        for r in response:
            # 첫 청크면 버킷 초기화, 이후에는 누적 결합(+=)로 완성도 올리기
            if ai_response_bucket is None:
                ai_response_bucket = r
            else:
                ai_response_bucket += r
            print(r.content, end='')            # 콘솔에 토큰/청크 단위 로그
            st.markdown(ai_response_bucket.content)  # 현재까지 누적된 전체 응답을 즉시 렌더링

    # 5) 최종 응답 텍스트를 메시지로 정리하여 세션 히스토리에 추가
    msg = ai_response_bucket.content
    st.session_state.messages.append(ai_response_bucket)  # 누적된 최종 AI 메시지 자체를 기록
    print('assistant:', msg)  # 콘솔 로그(디버깅용)


""" 
    이해 포인트 요약

RunnableWithMessageHistory: config={"configurable": {"session_id": ...}}로 세션을 식별하고, get_session_history 콜백을 통해 해당 세션의 InMemoryChatMessageHistory를 자동 로드/저장합니다. 덕분에 대화 문맥이 매 호출에 자동으로 포함됩니다.

Streamlit 상태 관리:

st.session_state["messages"]는 UI에 표시할 메시지(System/Human/AI)를 보관합니다.

st.session_state["store"]는 LangChain 전용 히스토리 객체(InMemoryChatMessageHistory)를 세션별로 보관합니다. (둘은 용도가 다릅니다)

스트리밍 표시 방식: with st.chat_message("assistant").empty():로 컨테이너를 잡고, 매 청크가 올 때마다 누적 응답을 st.markdown(...)으로 다시 그려 타자치는 듯한 효과를 냅니다.

키 관리: .env에 OPENAI_API_KEY를 넣고 load_dotenv()로 로드합니다. ChatOpenAI는 이를 자동으로 사용하므로 별도 인자 없이 동작합니다. """
