import streamlit as st
from datetime import datetime, timedelta
from streamlit_calendar import calendar

st.set_page_config(page_title="수행평가 캘린더", layout="wide")

st.title("📚 수행평가 캘린더")

# 세션 상태 초기화
if "tasks" not in st.session_state:
    st.session_state.tasks = []

# 입력 영역
st.subheader("수행평가 추가")

with st.form("task_form"):
    subject = st.text_input("과목명")
    title = st.text_input("수행평가 제목")
    date = st.date_input("날짜")

    submitted = st.form_submit_button("추가")

    if submitted:
        if subject and title:
            st.session_state.tasks.append(
                {
                    "subject": subject,
                    "title": title,
                    "date": date.strftime("%Y-%m-%d"),
                }
            )
            st.success("추가 완료!")
        else:
            st.error("과목명과 제목을 입력하세요.")

# 하루 전 알림
st.subheader("🔔 알림")

today = datetime.now().date()
tomorrow = today + timedelta(days=1)

found_notification = False

for task in st.session_state.tasks:
    task_date = datetime.strptime(task["date"], "%Y-%m-%d").date()

    if task_date == tomorrow:
        st.warning(
            f"내일 {task['subject']} - {task['title']} 수행평가가 있습니다!"
        )
        found_notification = True

if not found_notification:
    st.info("내일 예정된 수행평가가 없습니다.")

# 달력 이벤트 생성
events = []

for task in st.session_state.tasks:
    events.append(
        {
            "title": f"{task['subject']} | {task['title']}",
            "start": task["date"],
        }
    )

# 달력 표시
st.subheader("🗓️ 달력")

calendar_options = {
    "initialView": "dayGridMonth",
    "locale": "ko",
    "height": 700,
}

calendar(events=events, options=calendar_options)
