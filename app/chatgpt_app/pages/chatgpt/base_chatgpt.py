from typing import List, Optional, Tuple

import streamlit as st
from chatgpt_app.const import PageId
from chatgpt_app.langchain_wrapper import StreamlitCostCalcHandler, TokenCostProcess
from chatgpt_app.pages.base import BasePage
from chatgpt_app.prompts import PromptsLoader
from chatgpt_app.session import SessionKey, StreamlistSessionManager
from langchain.chat_models import ChatOpenAI
from langchain.schema import BaseMessage, SystemMessage
from streamlit.delta_generator import DeltaGenerator


class BaseChatGPTPage(BasePage):
    def __init__(self, page_id: PageId, title: str, sm: StreamlistSessionManager) -> None:
        super().__init__(page_id, title, sm)
        self.sidebar: Optional[DeltaGenerator] = None
        self.clear_button: Optional[bool] = None
        self.prompts_loader: PromptsLoader = PromptsLoader()

    def init_page(self) -> None:
        st.header(f"{self.title}  🤗")
        self.sidebar = st.sidebar
        self.sidebar.title("Options")
        self.clear_button = self.sidebar.button("Clear Conversation", key=SessionKey.CLEAR_BUTTON.name)

    def select_model(self) -> ChatOpenAI:
        model_name = st.sidebar.radio("Choose a model:", ("gpt-3.5-turbo", "gpt-3.5-turbo-16k-0613", "gpt-4"))
        self.sm.register_model_name(model_name)

        # スライダーを追加し、temperatureを0から2までの範囲で選択可能にする
        # 初期値は0.0、刻み幅は0.1とする
        temperature = st.sidebar.slider("Temperature:", min_value=0.0, max_value=2.0, value=0.0, step=0.01)

        llm = ChatOpenAI(  # type: ignore
            temperature=temperature,
            model_name=self.sm.get_model_name(),
            streaming=True,
        )
        return llm

    def init_messages(self, sm: StreamlistSessionManager) -> None:
        sm.clear_messages()
        sm.clear_costs()
        sm.add_message(SystemMessage(content="You are a helpful assistant."))

    def base_components(self) -> ChatOpenAI:
        self.init_page()
        llm = self.select_model()
        if self.clear_button:
            self.init_messages(self.sm)
        return llm

    def total_cost_component(self) -> None:
        costs = self.sm.get_costs()
        if self.sidebar is not None:
            self.sidebar.markdown("## Costs")
            self.sidebar.markdown(f"**Total cost: ${sum(costs):.5f}**")

    def get_streaming_answer(self, llm: ChatOpenAI, messages: List[BaseMessage]) -> Tuple[str, float]:
        token_cost_process = TokenCostProcess(llm.model_name)
        st_callback = StreamlitCostCalcHandler(st.container(), token_cost_process)
        answer = llm(messages, callbacks=[st_callback]).content
        cost = token_cost_process.total_cost
        return answer, cost
