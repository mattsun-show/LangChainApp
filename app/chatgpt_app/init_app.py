from chatgpt_app.app import MultiPageApp
from chatgpt_app.const import PageId
from chatgpt_app.pages.base import BasePage
from chatgpt_app.session import StreamlistSessionManager


def init_session() -> StreamlistSessionManager:
    session_manager = StreamlistSessionManager()
    return session_manager


def init_pages(sm: StreamlistSessionManager) -> list[BasePage]:
    from chatgpt_app.pages.chatbot import ChatBotPage

    pages = [ChatBotPage(page_id=PageId.CHATBOT, title="Chat Bot", sm=sm)]
    return pages


def init_app(sm: StreamlistSessionManager, pages: list[BasePage]) -> MultiPageApp:
    app = MultiPageApp(sm, pages)
    return app
