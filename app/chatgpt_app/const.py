from enum import Enum, auto


class SessionKey(Enum):
    # all pages
    PAGE_ID = auto()
    MESSAGES = auto()
    COSTS = auto()
    CLEAR_BUTTON = auto()
    MODEL_NAME = auto()
    # web summarize page
    URL_INPUT = auto()
    MAP_PROMPT_INPUT = auto()
    COMBINE_PROMPT_INPUT = auto()
    REFINE_PROMPT_INPUT = auto()
    # youtube summarize page
    MAX_TOKEN = auto()


class PageId(Enum):
    CHATBOT = auto()
    WEB_SUMMARIZE = auto()
    YOUTUBE_SUMMARIZE = auto()


class ChainType(Enum):
    MAP_REDUCE = "map_reduce"
    MAP_RERANK = "map_rerank"
    REFINE = "refine"
