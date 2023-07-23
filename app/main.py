import streamlit as st
from chatgpt_app.init_app import init_session
from chatgpt_app.logger import get_logger
from chatgpt_app.pages.chatbot import ChatBotPage

logger = get_logger(__name__)


if __name__ == "__main__":
    if not st.session_state.get("is_started", False):  # 初期化しているかの確認
        sm = init_session()
        st.session_state["is_started"] = True
        app = ChatBotPage(sm)
        st.session_state["app"] = app

    app = st.session_state.get("app", None)
    if app is not None:
        app.render()
