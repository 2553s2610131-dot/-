import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from streamlit_calendar import calendar

st.title("📚 수행평가 관리 앱")

# 세션 상태 초기화
if "tasks" not in st.session_state:
    st.session_state.tasks = []

# 수행평가 입력
subject = st.text_input("과목명")
title = st.text_input("수행평가 제목")
date = st.date_input("날짜")

if st.button("추가"):
    st.session_state.tasks.append({
        "subject": subject,
        "title": title,
        "date": str(date)
    })

# 알림 기능
today = datetime.today().date()
tomorrow = today + timedelta(days=1)

for task in st.session_state.tasks:
    task_date = datetime.strptime(task["date"], "%Y-%m-%d").date()

    if task_date == tomorrow:
        st.warning(
            f"⚠️ 내일 {task['subject']} 수행평가 ({task['title']}) 가 있어요!"
        )

# 달력 이벤트 생성
events = []

for task in st.session_state.tasks:
    events.append({
        "title": f"{task['subject']} - {task['title']}",
        "start": task["date"]
    })

calendar_options = {
    "initialView": "dayGridMonth",
    "height": 650,
}

calendar(events=events, options=calendar_options)
