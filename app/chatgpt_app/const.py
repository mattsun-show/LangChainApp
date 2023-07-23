from enum import Enum, auto


class SessionKey(Enum):
    PAGE_ID = auto()
    MESSAGES = auto()
    COSTS = auto()


class PageId(Enum):
    CHATBOT = auto()
