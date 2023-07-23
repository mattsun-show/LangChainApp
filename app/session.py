from typing import List

import streamlit as st
from const import SessionKey
from langchain.schema import BaseMessage
from logger import get_logger

logger = get_logger()


class StreamlistSessionManager:
    def __init__(self) -> None:
        self._session_state = st.session_state
        self._session_state[SessionKey.MESSAGES.name] = []
        self._session_state[SessionKey.COSTS.name] = []

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
