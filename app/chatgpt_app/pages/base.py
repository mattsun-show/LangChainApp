from chatgpt_app.const import PageId
from chatgpt_app.session import StreamlistSessionManager


class BasePage:
    def __init__(self, page_id: PageId, title: str, sm: StreamlistSessionManager) -> None:
        self.page_id = page_id
        self.title = title
        self.sm = sm

    def render(self) -> None:
        raise NotImplementedError("Please overwrite render function.")
