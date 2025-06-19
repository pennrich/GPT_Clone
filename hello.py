import openai
import streamlit as st

st.title("ChatGPT-like Clone")

# API 키 설정
openai.api_key = st.secrets["OPENAI_API_KEY"]

# 세션 상태 초기화
if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "gpt-3.5-turbo"

if "messages" not in st.session_state:
    st.session_state.messages = []

# 이전 메시지 렌더링
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 입력 및 응답 처리
if prompt := st.chat_input("What is up?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

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
            if chunk.choices[0].delta and hasattr(chunk.choices[0].delta, "content"):
                content = chunk.choices[0].delta.content
                response += content
                st.markdown(response + "▌")
        st.markdown(response)

    st.session_state.messages.append({"role": "assistant", "content": response})
