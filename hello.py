import openai
import streamlit as st

# 앱 제목
st.title("ChatGPT-like Clone")

# OpenAI API 키 설정
openai.api_key = st.secrets["OPENAI_API_KEY"]

# 모델 기본값 설정
if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "gpt-3.5-turbo"

# 메시지 히스토리 초기화
if "messages" not in st.session_state:
    st.session_state.messages = []

# 기존 메시지 출력
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 사용자 입력 받기
if prompt := st.chat_input("What is up?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # OpenAI 응답 스트리밍
    with st.chat_message("assistant"):
        response = ""
        stream = openai.chat.completions.create(
            model=st.session_state["openai_model"],
            messages=[
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.messages
            ],
            stream=True,
        )
        for chunk in stream:
            content = chunk.choices[0].delta.get("content", "")
            response += content
            st.markdown(response + "▌")
        st.markdown(response)

    # 응답 저장
    st.session_state.messages.append({"role": "assistant", "content": response})
