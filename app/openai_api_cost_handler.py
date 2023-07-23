from typing import Any, Dict, List, Optional
from uuid import UUID

import tiktoken
from langchain.callbacks.streamlit.streamlit_callback_handler import (
    LLMThoughtLabeler,
    StreamlitCallbackHandler,
)
from langchain.chat_models.openai import _convert_message_to_dict
from langchain.schema import LLMResult
from langchain.schema.messages import BaseMessage
from streamlit.delta_generator import DeltaGenerator

MODEL_COST_PER_1K_TOKENS = {
    "gpt-4": 0.03,
    "gpt-4-0314": 0.03,
    "gpt-4-completion": 0.06,
    "gpt-4-0314-completion": 0.06,
    "gpt-4-32k": 0.06,
    "gpt-4-32k-0314": 0.06,
    "gpt-4-32k-completion": 0.12,
    "gpt-4-32k-0314-completion": 0.12,
    "gpt-3.5-turbo": 0.002,
    "gpt-3.5-turbo-0301": 0.002,
    "text-ada-001": 0.0004,
    "ada": 0.0004,
    "text-babbage-001": 0.0005,
    "babbage": 0.0005,
    "text-curie-001": 0.002,
    "curie": 0.002,
    "text-davinci-003": 0.02,
    "text-davinci-002": 0.02,
    "code-davinci-002": 0.02,
}


def num_tokens_from_messages(messages, model="gpt-3.5-turbo-0613"):
    """Return the number of tokens used by a list of messages."""
    try:
        encoding = tiktoken.encoding_for_model(model)
    except KeyError:
        print("Warning: model not found. Using cl100k_base encoding.")
        encoding = tiktoken.get_encoding("cl100k_base")

    if model in {
        "gpt-3.5-turbo-0613",
        "gpt-3.5-turbo-16k-0613",
        "gpt-4-0314",
        "gpt-4-32k-0314",
        "gpt-4-0613",
        "gpt-4-32k-0613",
    }:
        tokens_per_message = 3
        tokens_per_name = 1
    elif model == "gpt-3.5-turbo-0301":
        tokens_per_message = (
            4  # every message follows <|start|>{role/name}\n{content}<|end|>\n
        )
        tokens_per_name = -1  # if there's a name, the role is omitted
    elif "gpt-3.5-turbo" in model:
        print(
            "Warning: gpt-3.5-turbo may update over time. "
            "Returning num tokens assuming gpt-3.5-turbo-0613."
        )
        return num_tokens_from_messages(messages, model="gpt-3.5-turbo-0613")
    elif "gpt-4" in model:
        print(
            "Warning: gpt-4 may update over time. "
            "Returning num tokens assuming gpt-4-0613."
        )
        return num_tokens_from_messages(messages, model="gpt-4-0613")
    else:
        raise NotImplementedError(
            f"num_tokens_from_messages() is not implemented for model {model}. "
            "See https://github.com/openai/openai-python/blob/main/chatml.md "
            "for information on how messages are converted to tokens."
        )

    num_tokens = 0
    for message in messages:
        num_tokens += tokens_per_message
        for key, value in message.items():
            num_tokens += len(encoding.encode(value))
            if key == "name":
                num_tokens += tokens_per_name
    num_tokens += 3  # every reply is primed with <|start|>assistant<|message|>
    return num_tokens


class TokenCostProcess:
    total_tokens: int = 0
    prompt_tokens: int = 0
    completion_tokens: int = 0
    successful_requests: int = 0

    def __init__(self, model):
        self.model = model

    def sum_prompt_tokens(self, tokens: int):
        self.prompt_tokens = self.prompt_tokens + tokens
        self.total_tokens = self.total_tokens + tokens

    def sum_completion_tokens(self, tokens: int):
        self.completion_tokens = self.completion_tokens + tokens
        self.total_tokens = self.total_tokens + tokens

    def sum_successful_requests(self, requests: int):
        self.successful_requests = self.successful_requests + requests

    @property
    def total_cost(self) -> float:
        return MODEL_COST_PER_1K_TOKENS[self.model] * self.total_tokens / 1000

    @property
    def cost_summary(self) -> str:
        return (
            f"Tokens Used: {self.total_tokens}\n"
            f"\tPrompt Tokens: {self.prompt_tokens}\n"
            f"\tCompletion Tokens: {self.completion_tokens}\n"
            f"Successful Requests: {self.successful_requests}\n"
            f"Total Cost (USD): {self.total_cost}"
        )


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
        self.encoding = tiktoken.encoding_for_model(
            self.token_cost_process.model
        )
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
        msg_dicts = list(map(_convert_message_to_dict, messages[0]))
        token_num = num_tokens_from_messages(
            msg_dicts, self.token_cost_process.model
        )
        self.token_cost_process.sum_prompt_tokens(token_num)
        super().on_chat_model_start(serialized, messages, **kwargs)

    def on_llm_new_token(self, token: str, **kwargs) -> None:
        # print(token)
        self.token_cost_process.sum_completion_tokens(
            len(self.encoding.encode(token))
        )
        super().on_llm_new_token(token, **kwargs)

    def on_llm_end(self, response: LLMResult, **kwargs: Any) -> None:
        self.token_cost_process.sum_successful_requests(1)
        super().on_llm_end(response, **kwargs)
