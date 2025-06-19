from openai import OpenAI, RateLimitError
import streamlit as st

st.title("ChatGPT-like clone")

# API 키 로드
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# 모델 설정
if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "gpt-3.5-turbo"

# 메시지 세션 초기화
if "messages" not in st.session_state:
    st.session_state.messages = []

# 이전 메시지 렌더링
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 사용자 입력 처리
if prompt := st.chat_input("What is up?"):
    # 사용자 메시지 저장 및 표시
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 어시스턴트 응답 처리
    with st.chat_message("assistant"):
        try:
            # 스트리밍 응답 생성
            stream = client.chat.completions.create(
                model=st.session_state["openai_model"],
                messages=[
                    {"role": m["role"], "content": m["content"]}
                    for m in st.session_state.messages
                ],
                stream=True,
            )

            # 응답을 점차 출력하고, 전체 텍스트 누적
            full_response = ""
            placeholder = st.empty()

            for chunk in stream:
                # 안전하게 content 추출
                content = getattr(chunk.choices[0].delta, "content", None)
                if content:
                    full_response += content
                    placeholder.markdown(full_response)

            # 응답 저장
            st.session_state.messages.append(
                {"role": "assistant", "content": full_response}
            )

        except RateLimitError:
            st.error("⚠️ 요청이 너무 많습니다. 잠시 후 다시 시도해 주세요.")
        except Exception as e:
            st.error(f"❌ 오류 발생: {e}")
