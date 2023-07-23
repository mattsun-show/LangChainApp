from chatgpt_app.session import StreamlistSessionManager


class BasePage:
    def __init__(self, sm: StreamlistSessionManager) -> None:
        self.sm = sm

    def render(self) -> None:
        raise NotImplementedError("Please overwrite render function.")
