from openai import OpenAI, RateLimitError
import streamlit as st
from datetime import datetime

# 페이지 설정
st.set_page_config(page_title="나만의 ChatGPT", layout="wide")

# 💾 API 키 로드
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# 🧠 모델 설정
if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "gpt-4o"

# 💬 대화 저장소 초기화
if "conversations" not in st.session_state:
    st.session_state["conversations"] = {}

# ▶️ 현재 대화 ID 설정
if "current_conversation" not in st.session_state:
    default_name = datetime.now().strftime("대화 %Y-%m-%d %H:%M:%S")
    st.session_state["current_conversation"] = default_name
    st.session_state["conversations"][default_name] = []

# 🧭 사이드바: 대화 선택 및 새로 만들기
with st.sidebar:
    st.header("🗂️ 대화 이력")
    selected = st.radio(
        "기존 대화 선택",
        options=list(st.session_state["conversations"].keys()),
        index=list(st.session_state["conversations"].keys()).index(st.session_state["current_conversation"]),
    )
    if selected != st.session_state["current_conversation"]:
        st.session_state["current_conversation"] = selected

    if st.button("➕ 새 대화 시작"):
        new_name = datetime.now().strftime("대화 %Y-%m-%d %H:%M:%S")
        st.session_state["conversations"][new_name] = []
        st.session_state["current_conversation"] = new_name

# 👉 채팅 영역: 가운데만 사용
left_col, center_col, right_col = st.columns([1, 2, 1])

with center_col:
    # ✅ 입력창 CSS 스타일 조정
    st.markdown("""
        <style>
        textarea[data-testid="stChatInput"] {
            width: 400px !important;
            height: 200px !important;  /* ✅ 이 줄 추가 */
            margin: auto !important;
        }
        </style>
    """, unsafe_allow_html=True)

    # 여백
    st.markdown("<div style='height: 800px;'></div>", unsafe_allow_html=True)

    st.title("나만의 ChatGPT")

    # 현재 대화 불러오기
    messages = st.session_state["conversations"][st.session_state["current_conversation"]]

    # 💬 이전 메시지 출력
    for message in messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # 📥 사용자 입력 및 처리
    if prompt := st.chat_input("메시지를 입력하세요."):
        messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # 🤖 어시스턴트 응답
        with st.chat_message("assistant"):
            try:
                stream = client.chat.completions.create(
                    model=st.session_state["openai_model"],
                    messages=[{"role": m["role"], "content": m["content"]} for m in messages],
                    stream=True,
                )

                full_response = ""
                placeholder = st.empty()

                for chunk in stream:
                    content = getattr(chunk.choices[0].delta, "content", None)
                    if content:
                        full_response += content
                        placeholder.markdown(full_response)

                messages.append({"role": "assistant", "content": full_response})

            except RateLimitError:
                st.error("⚠️ 요청이 너무 많습니다. 잠시 후 다시 시도해 주세요.")
            except Exception as e:
                st.error(f"❌ 오류 발생: {e}")
