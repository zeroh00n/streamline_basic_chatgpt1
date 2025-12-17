import streamlit as st

from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, ToolMessage



#openai_api_key가져오기
from openai import OpenAI  # 주석처리
from dotenv import load_dotenv
import os
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")  # 환경 변수에서 API 키 가져오기
#openai_api_key가져오기


# 모델 초기화
llm = ChatOpenAI(model="gpt-4o-mini")
# llm = ChatOpenAI(model="gpt-4o-mini", api_key=api_key)
# 사용자의 메시지 처리하기 위한 함수
def get_ai_response(messages):
    response = llm.stream(messages)

    for chunk in response:
        yield chunk

# Streamlit 앱
st.title("💬 langchain_streamlit_tool_0.py")
print("")
st.title("GPT-4o Langchain Chat")

# 스트림릿 session_state에 메시지 저장
if "messages" not in st.session_state:
    st.session_state["messages"] = [
        SystemMessage("너는 사용자를 돕기 위해 최선을 다하는 인공지능 봇이다. "),  
        AIMessage("How can I help you?")
    ]

# 스트림릿 화면에 메시지 출력
for msg in st.session_state.messages:
    if msg.content:
        if isinstance(msg, SystemMessage):
            st.chat_message("system").write(msg.content)
        elif isinstance(msg, AIMessage):
            st.chat_message("assistant").write(msg.content)
        elif isinstance(msg, HumanMessage):
            st.chat_message("user").write(msg.content)

# 사용자 입력 처리
if prompt := st.chat_input():
    st.chat_message("user").write(prompt) # 사용자 메시지 출력
    st.session_state.messages.append(HumanMessage(prompt)) # 사용자 메시지 저장

    response = get_ai_response(st.session_state["messages"])
    
    result = st.chat_message("assistant").write_stream(response) # AI 메시지 출력
    st.session_state["messages"].append(AIMessage(result)) # AI 메시지 저장    
