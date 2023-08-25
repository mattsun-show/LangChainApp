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
        self._session_state[SessionKey.MODEL_NAME] = ""
        self._session_state[SessionKey.URL_INPUT.name] = ""
        self._session_state[SessionKey.MAX_TOKEN.name] = 0
        self._session_state[SessionKey.MAP_PROMPT_INPUT] = ""
        self._session_state[SessionKey.COMBINE_PROMPT_INPUT] = ""
        self._session_state[SessionKey.REFINE_PROMPT_INPUT] = ""

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
    # model_name
    # -----------------------
    def get_model_name(self) -> str:
        return self._session_state[SessionKey.MODEL_NAME.name]

    def register_model_name(self, model_name: str) -> None:
        self._session_state[SessionKey.MODEL_NAME.name] = model_name

    # -----------------------
    # url_input
    # -----------------------
    def clear_url_input(self) -> None:
        self._session_state[SessionKey.URL_INPUT.name] = ""

    # -----------------------
    # map_prompt_input
    # -----------------------
    def set_map_prompt_input(self, prompt: str) -> None:
        self._session_state[SessionKey.MAP_PROMPT_INPUT.name] = prompt

    def get_map_prompt_input(self) -> str:
        return self._session_state[SessionKey.MAP_PROMPT_INPUT.name]

    # -----------------------
    # combine_prompt_input
    # -----------------------
    def set_combine_prompt_input(self, prompt: str) -> None:
        self._session_state[SessionKey.COMBINE_PROMPT_INPUT.name] = prompt

    def get_combine_prompt_input(self) -> str:
        return self._session_state[SessionKey.COMBINE_PROMPT_INPUT.name]

    # -----------------------
    # refine_prompt_input
    # -----------------------
    def set_refine_prompt_input(self, prompt: str) -> None:
        self._session_state[SessionKey.REFINE_PROMPT_INPUT.name] = prompt

    def get_refine_prompt_input(self) -> str:
        return self._session_state[SessionKey.REFINE_PROMPT_INPUT.name]

    # -----------------------
    # max_token
    # -----------------------
    def get_max_token(self) -> int:
        return self._session_state[SessionKey.MAX_TOKEN.name]

    def register_max_token(self, max_token_num: int) -> None:
        self._session_state[SessionKey.MAX_TOKEN.name] = max_token_num
