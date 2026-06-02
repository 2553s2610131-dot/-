import streamlit as st
import google.generativeai as genai

# 1. 페이지 설정 및 제목
st.set_page_config(page_title="⚽ 축구 분석 AI 챗봇", page_icon="⚽", layout="centered")
st.title("⚽ 축구 분석 AI 챗봇")
st.caption("전술, 경기 분석, 선수 스탯 등 축구에 대한 모든 것을 물어보세요!")

# 2. Streamlit Secrets에서 API 키 불러오기 및 설정
try:
    # Streamlit Cloud 배포 환경 및 로컬 .streamlit/secrets.toml 대응
    gemini_api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=gemini_api_key)
except KeyError:
    st.error("❌ API 키를 찾을 수 없습니다. Streamlit Secrets에 'GEMINI_API_KEY'를 설정해주세요.")
    st.stop()

# 3. 세션 상태(Session State)로 채팅 기록 초기화
if "messages" not in st.session_state:
    st.session_state.messages = []

# 4. 기존 채팅 기록 화면에 출력
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 5. 사용자 입력 받기
if user_input := st.chat_input("예: 현대 축구에서 인버티드 풀백의 역할은 무엇인가요?"):
    
    # 사용자 메시지 화면에 표시 및 세션에 저장
    st.chat_message("user").markdown(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    # 6. AI 답변 생성 및 오류 처리
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        
        try:
            # gemini-2.5-flash-lite 모델 설정
            # 축구 분석가로서의 전문성을 부여하기 위한 system_instruction 추가
            model = genai.GenerativeModel(
                model_name="gemini-2.5-flash-lite",
                system_instruction="당신은 전문적인 축구 분석가이자 전술가입니다. 사용자의 질문에 대해 데이터, 전술적 관점, 역사적 배경을 바탕으로 친절하고 깊이 있게 답변해주세요."
            )
            
            # 대화 맥락을 유지하기 위해 기존 대화 기록을 포함하여 메시지 구성
            # Gemini API 형식에 맞게 변환 (user -> user, assistant -> model)
            history = []
            for msg in st.session_state.messages[:-1]:  # 방금 넣은 user_input 제외한 이전 기록
                role = "user" if msg["role"] == "user" else "model"
                history.append({"role": role, "parts": [msg["content"]]})
            
            # 채팅 세션 시작
            chat = model.start_chat(history=history)
            
            # 답변 생성 (스트리밍 방식 적용으로 더 자연스러운 UI 제공)
            full_response = ""
            response = chat.send_message(user_input, stream=True)
            
            for chunk in response:
                full_response += chunk.text
                message_placeholder.markdown(full_response + "▌")
                
            message_placeholder.markdown(full_response)
            
            # AI 답변을 세션에 저장
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            
        except genai.types.generation_types.BlockedPromptException:
            st.error("⚠️ 안전 정책에 의해 답변을 생성할 수 없는 요청입니다.")
        except Exception as e:
            st.error(f"❌ 오류가 발생했습니다: {str(e)}")
            st.info("API 키가 올바른지, 혹은 네트워크 상태를 확인해주세요.")
