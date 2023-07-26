from typing import List

import streamlit as st
from chatgpt_app.const import SessionKey
from chatgpt_app.logger import get_logger
from langchain.schema import BaseMessage

logger = get_logger()


class StreamlistSessionManager:
    def __init__(self) -> None:
        self._session_state = st.session_state
        self._session_state[SessionKey.MESSAGES.name] = []
        self._session_state[SessionKey.COSTS.name] = []
        self._session_state[SessionKey.URL_INPUT.name] = ""

    # -----------------------
    # messages
    # -----------------------
    def get_messages(self) -> List[BaseMessage]:
        return self._session_state[SessionKey.MESSAGES.name]

    def add_message(self, message: BaseMessage) -> None:
        self._session_state[SessionKey.MESSAGES.name].append(message)

    def clear_messages(self) -> None:
        self._session_state[SessionKey.MESSAGES.name] = []

    # -----------------------
    # costs
    # -----------------------
    def get_costs(self) -> List[float]:
        return self._session_state[SessionKey.COSTS.name]

    def add_cost(self, cost: float) -> None:
        self._session_state[SessionKey.COSTS.name].append(cost)

    def clear_costs(self) -> None:
        self._session_state[SessionKey.COSTS.name] = []

    # -----------------------
    # url_input
    # -----------------------
    def clear_url_input(self) -> None:
        self._session_state[SessionKey.URL_INPUT.name] = ""
