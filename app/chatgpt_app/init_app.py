from chatgpt_app.session import StreamlistSessionManager


def init_session() -> StreamlistSessionManager:
    session_manager = StreamlistSessionManager()
    return session_manager
