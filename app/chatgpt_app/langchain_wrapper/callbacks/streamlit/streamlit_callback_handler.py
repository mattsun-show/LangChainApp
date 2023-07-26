from typing import Any, Dict, List, Optional

from chatgpt_app.langchain_wrapper.token_cost_process import TokenCostProcess
from chatgpt_app.logger import get_logger
from langchain.callbacks.streamlit.streamlit_callback_handler import LLMThoughtLabeler, StreamlitCallbackHandler
from langchain.schema import LLMResult
from langchain.schema.messages import BaseMessage
from streamlit.delta_generator import DeltaGenerator

logger = get_logger()


class StreamlitCostCalcHandler(StreamlitCallbackHandler):
    def __init__(
        self,
        parent_container: DeltaGenerator,
        token_cost_process: TokenCostProcess,
        *,
        max_thought_containers: int = 4,
        expand_new_thoughts: bool = True,
        collapse_completed_thoughts: bool = True,
        thought_labeler: Optional[LLMThoughtLabeler] = None,
    ):
        self.token_cost_process = token_cost_process
        super().__init__(
            parent_container,
            max_thought_containers=max_thought_containers,
            expand_new_thoughts=expand_new_thoughts,
            collapse_completed_thoughts=collapse_completed_thoughts,
            thought_labeler=thought_labeler,
        )

    def on_chat_model_start(
        self,
        serialized: Dict[str, Any],
        messages: List[List[BaseMessage]],
        **kwargs: Any,
    ) -> None:
        """Run when a chat model starts running."""
        # logger.info(messages)
        token_num = self.token_cost_process.tokens_from_base_messages(messages[0])
        self.token_cost_process.sum_prompt_tokens(token_num)
        super().on_chat_model_start(serialized, messages, **kwargs)

    def on_llm_new_token(self, token: str, **kwargs: Any) -> None:
        # logger.info(token)
        token_num = self.token_cost_process.tokens_from_string(token)
        self.token_cost_process.sum_completion_tokens(token_num)
        super().on_llm_new_token(token, **kwargs)

    def on_llm_end(self, response: LLMResult, **kwargs: Any) -> None:
        # logger.info("llm end")
        self.token_cost_process.sum_successful_requests(1)
        super().on_llm_end(response, **kwargs)
        super()._require_current_thought()._container.update(
            new_label=self._thought_labeler.get_final_agent_thought_label()
        )
