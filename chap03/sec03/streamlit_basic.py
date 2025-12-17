import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv
import os

# ---------------------------------
# 기본 설정
# ---------------------------------
st.set_page_config(
    page_title="김영훈의 챗봇",
    page_icon="💬",
    layout="centered"
)

load_dotenv()

# ---------------------------------
# 사이드바
# ---------------------------------
with st.sidebar:
    st.header("⚙️ 설정")

    openai_api_key = os.getenv("OPENAI_API_KEY")

    if openai_api_key:
        st.success("OpenAI API Key 연결됨")
    else:
        st.warning("API Key가 없습니다")

    st.markdown("---")
    st.markdown("[Youtube](https:/www.youtube.com)")

# ---------------------------------
# 이름 입력 (session_state로 관리)
# ---------------------------------
name = st.text_input(
    "👋 뭐라고 불러드릴까요?",
    key="username",
    placeholder="이름을 입력하세요"
)

st.title("💬 김영훈의 챗봇")
st.caption("Streamlit + OpenAI로 만든 간단한 챗봇")

# ---------------------------------
# 세션 상태 초기화
# ---------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

# 이름이 처음 입력됐을 때만 인사 추가
if st.session_state.username and len(st.session_state.messages) == 0:
    st.session_state.messages.append({
        "role": "assistant",
        "content": f"{st.session_state.username}님, 무엇을 도와드릴까요?"
    })

# ---------------------------------
# 대화 기록 출력
# ---------------------------------
for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.chat_message("user", avatar="🧑").write(msg["content"])
    else:
        st.chat_message("assistant", avatar="🤖").write(msg["content"])

# ---------------------------------
# 사용자 입력 & AI 응답
# ---------------------------------
if prompt := st.chat_input("메시지를 입력하세요"):
    if not openai_api_key:
        st.info("사이드바에 OpenAI API Key를 설정해주세요.")
        st.stop()

    client = OpenAI(api_key=openai_api_key)

    # 사용자 메시지
    st.session_state.messages.append({
        "role": "user",
        "content": prompt
    })
    st.chat_message("user", avatar="🧑").write(prompt)

    # AI 응답
    with st.chat_message("assistant", avatar="🤖"):
        with st.spinner("생각 중..."):
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=st.session_state.messages
            )
            msg = response.choices[0].message.content

    st.session_state.messages.append({
        "role": "assistant",
        "content": msg
    })
    st.write(msg)
