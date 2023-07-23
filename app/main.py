import streamlit as st
from chatgpt_app.init_app import init_app, init_pages, init_session
from chatgpt_app.logger import get_logger

logger = get_logger(__name__)


if __name__ == "__main__":
    st.set_page_config(page_title="My Great ChatGPT", page_icon="🤗")
    if not st.session_state.get("is_started", False):  # 初期化しているかの確認
        sm = init_session()
        pages = init_pages(sm)
        app = init_app(sm, pages)
        st.session_state["is_started"] = True
        st.session_state["app"] = app

    app = st.session_state.get("app", None)
    if app is not None:
        app.render()
