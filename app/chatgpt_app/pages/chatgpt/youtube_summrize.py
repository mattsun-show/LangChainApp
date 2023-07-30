from typing import List, Tuple

import streamlit as st
from chatgpt_app.const import SessionKey
from chatgpt_app.langchain_wrapper import StreamlitCostCalcHandler, TokenCostProcess
from chatgpt_app.logger import get_logger
from chatgpt_app.pages.chatgpt.base_chatgpt import BaseChatGPTPage
from chatgpt_app.session import StreamlistSessionManager
from langchain.chains.summarize import load_summarize_chain
from langchain.chat_models import ChatOpenAI
from langchain.docstore.document import Document
from langchain.document_loaders import YoutubeLoader
from langchain.prompts import PromptTemplate
from streamlit_extras.stoggle import stoggle

logger = get_logger(__name__)


class YouTubeSummarizePage(BaseChatGPTPage):
    def init_messages(self, sm: StreamlistSessionManager) -> None:
        sm.clear_url_input()
        return super().init_messages(sm)

    def get_url_input(self) -> str:
        url = st.text_input("YouTube URL: ", key=SessionKey.URL_INPUT.name)
        return url

    def validate_url(self, url: str) -> bool:
        return "https://www.youtube.com/watch?" in url

    def get_document(self, url: str) -> List[Document]:
        with st.spinner("Fetching Content ..."):
            loader = YoutubeLoader.from_youtube_url(url, add_video_info=True, language=["en", "ja"])
            return loader.load()

    def summarize(self, llm: ChatOpenAI, docs: List[Document]) -> Tuple[str, float]:
        prompt_template = self.prompts_loader.youtube_summarize_template()
        PROMPT = PromptTemplate(template=prompt_template, input_variables=["text"])

        chain = load_summarize_chain(llm, chain_type="stuff", verbose=True, prompt=PROMPT)
        token_cost_process = TokenCostProcess(llm.model_name)
        st_callback = StreamlitCostCalcHandler(st.container(), token_cost_process)
        response = chain({"input_documents": docs}, return_only_outputs=True, callbacks=[st_callback])

        answer = response["output_text"]
        cost = token_cost_process.total_cost
        return answer, cost

    def render(self) -> None:
        llm = self.base_components()

        url_container = st.container()
        response_container = st.container()

        document = None
        with url_container:
            url = self.get_url_input()
            is_valid_url = self.validate_url(url)
            if not is_valid_url:
                st.write("Please input valid url")
            else:
                st.video(url)
                document = self.get_document(url)

        if document:
            with response_container:
                st.markdown("## Summary")
                answer, cost = self.summarize(llm, document)
                self.sm.add_cost(cost)
                st.markdown("---")
                st.markdown("## Original Text")
                stoggle("Original Text", document)

        # 合計コストの再取得、表示
        self.total_cost_component()
