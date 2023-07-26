from typing import List

import streamlit as st
from chatgpt_app.const import SessionKey
from chatgpt_app.pages.base import BasePage
from chatgpt_app.session import StreamlistSessionManager


class MultiPageApp:
    def __init__(self, sm: StreamlistSessionManager, pages: List[BasePage], nav_label: str = "ページ一覧") -> None:
        self.sm = sm
        self.pages = {page.page_id: page for page in pages}
        self.nav_label = nav_label

    def init_session(self) -> None:
        self.sm = StreamlistSessionManager()

    def render(self) -> None:
        # ページ選択ボックス
        page_id = st.sidebar.selectbox(
            self.nav_label,
            list(self.pages.keys()),
            format_func=lambda page_id: self.pages[page_id].title,
            key=SessionKey.PAGE_ID.name,
            on_change=self.init_session,
        )

        # ページ描画
        self.pages[page_id].render()
