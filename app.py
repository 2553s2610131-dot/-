import streamlit as st
from google import genai
from google.genai import types
from google.genai.errors import APIError

# 페이지 설정
st.set_page_config(page_title="공부 상담 챗봇", page_icon="📚", layout="centered")

# Streamlit Secrets에서 API 키 불러오기
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    client = genai.Client(api_key=api_key)
except KeyError:
    st.error("🔑 Streamlit Secrets에 'GEMINI_API_KEY'가 설정되지 않았습니다. .streamlit/secrets.toml 파일을 확인해주세요.")
    st.stop()

# 세션 상태(Chat History) 초기화
if "messages" not in st.session_state:
    st.session_state.messages = []

# 앱 제목 및 설명
st.title("📚 무엇이든 물어보세요! 공부 상담소")
st.caption("공부 방법, 시간 관리, 슬럼프 극복 등 공부에 대한 고민을 나누어보세요.")

# 기존 대화 기록 출력
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 사용자 입력 받기
if user_input := st.chat_input("공부하면서 어떤 점이 가장 힘드신가요?"):
    
    # 1. 사용자 메시지 화면에 표시 및 저장
    with st.chat_message("user"):
        st.markdown(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    # 2. 챗봇 답변 생성 및 오류 처리
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        
        try:
            # 페르소나 부여를 위한 시스템 지침(System Instruction) 설정
            system_instruction = (
                "당신은 친절하고 전문적인 공부 상담 멘토입니다. "
                "학생들의 학습 고민(시간 관리, 집중력, 과목별 공부법 등)을 경청하고, "
                "공감해주며, 실질적이고 단계적인 해결책을 제시해주세요. "
                "답변은 친근하고 격려하는 어조로 작성해주세요."
            )
            
            # API 모델 호출용 메시지 구조 변환 (이전 대화 기록 포함)
            contents = []
            for msg in st.session_state.messages:
                # SDK 구조에 맞게 user/model로 역할 매핑
                role = "user" if msg["role"] == "user" else "model"
                contents.append(types.Content(
                    role=role,
                    parts=[types.Part.from_text(text=msg["content"])]
                ))
            
            # API 호출 (gemini-2.5-flash-lite 사용)
            response = client.models.generate_content(
                model='gemini-2.5-flash-lite',
                contents=contents,
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    temperature=0.7,
                )
            )
            
            # 결과 출력 및 저장
            ai_response = response.text
            message_placeholder.markdown(ai_response)
            st.session_state.messages.append({"role": "assistant", "content": ai_response})
            
        except APIError as e:
            # Gemini API 관련 오류 처리
            error_msg = f"❌ Gemini API 오류가 발생했습니다: {e.message}"
            message_placeholder.error(error_msg)
        except Exception as e:
            # 기타 일반 오류 처리
            error_msg = f"⚠️ 알 수 없는 오류가 발생했습니다: {str(e)}"
            message_placeholder.error(error_msg)
