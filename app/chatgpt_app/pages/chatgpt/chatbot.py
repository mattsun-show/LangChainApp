from copy import deepcopy
from typing import List

import streamlit as st
from chatgpt_app.pages.chatgpt.base_chatgpt import BaseChatGPTPage
from langchain.schema import AIMessage, BaseMessage, HumanMessage


class ChatBotPage(BaseChatGPTPage):
    def message_history(self, messages: List[BaseMessage], costs: List[float]) -> None:
        for message in messages:
            if isinstance(message, AIMessage):
                with st.chat_message("assistant"):
                    st.markdown(message.content)
                    # コスト表示
                    st.markdown(f"cost: ${costs.pop(0):.5f}")
            elif isinstance(message, HumanMessage):
                with st.chat_message("user"):
                    st.markdown(message.content)
            else:  # isinstance(message, SystemMessage):
                st.write(f"System message: {message.content}")

    def render(self) -> None:
        self.init_page()
        llm = self.select_model()
        self.init_messages(self.sm)

        # ユーザー入力欄を一番上に置いておく
        container = st.container()

        # チャット履歴の表示
        costs = deepcopy(self.sm.get_costs())
        messages = self.sm.get_messages()
        self.message_history(messages, costs)

        # ユーザーの入力を監視
        with container:
            with st.form(key="my_form", clear_on_submit=True):
                user_input = st.text_area(label="Message: ", key="input", height=100)
                submit_button = st.form_submit_button(label="Send")

        # NOTE: streamlit 1.26.0 待ち
        # if user_input := st.chat_input("聞きたいことを入力してね！"):
        if submit_button and user_input:
            self.sm.add_message(HumanMessage(content=user_input))
            # streaming表示
            st.chat_message("user").markdown(user_input)
            with st.chat_message("assistant"):
                answer, cost = self.get_streaming_answer(llm, messages)
                # コスト表示
                st.markdown(f"cost: ${cost:.5f}")
                self.sm.add_message(AIMessage(content=answer))
                self.sm.add_cost(cost)
            # 合計コストの再取得、表示
            costs = self.sm.get_costs()
            st.sidebar.markdown("## Costs")
            st.sidebar.markdown(f"**Total cost: ${sum(costs):.5f}**")
