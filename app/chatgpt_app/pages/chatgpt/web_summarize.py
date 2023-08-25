from typing import List, Optional, Tuple
from urllib.parse import urlparse

import requests
import streamlit as st
from bs4 import BeautifulSoup
from chatgpt_app.const import SessionKey
from chatgpt_app.langchain_wrapper import TokenCostProcess
from chatgpt_app.logger import get_logger
from chatgpt_app.pages.chatgpt.base_chatgpt import BaseChatGPTPage
from chatgpt_app.session import StreamlistSessionManager
from langchain.chains import MapReduceDocumentsChain, ReduceDocumentsChain
from langchain.chains.combine_documents.stuff import StuffDocumentsChain
from langchain.chains.llm import LLMChain
from langchain.chains.summarize import load_summarize_chain
from langchain.chat_models import ChatOpenAI
from langchain.docstore.document import Document
from langchain.prompts import PromptTemplate
from langchain.text_splitter import RecursiveCharacterTextSplitter
from streamlit_extras.stoggle import stoggle

logger = get_logger(__name__)


class WebSummarizePage(BaseChatGPTPage):
    def select_model(self) -> ChatOpenAI:
        # 本文以外の指示のtoken数
        self.sm.register_max_token(1000)
        return super().select_model()

    def init_messages(self, sm: StreamlistSessionManager) -> None:
        sm.clear_url_input()
        return super().init_messages(sm)

    def get_url_input(self) -> str:
        url = st.text_input("URL: ", key=SessionKey.URL_INPUT.name)
        return url

    def validate_url(self, url: str) -> bool:
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except ValueError:
            return False

    def get_content(self, url: str) -> Optional[str]:
        try:
            with st.spinner("Fetching Content ..."):
                response = requests.get(url)
                soup = BeautifulSoup(response.text, "html.parser")
                # fetch text from main (change the below code to filter page)
                if soup.main:
                    elements = soup.main.get_text()
                elif soup.article:
                    elements = soup.article.get_text()
                else:
                    elements = soup.body.get_text()
                text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
                    model_name=self.sm.get_model_name(), chunk_size=self.sm.get_max_token(), chunk_overlap=0
                )
                list = text_splitter.split_text(elements)
                return text_splitter.create_documents(list)
        except Exception:
            st.write("something wrong")
            return None

    def summarize(
        self, llm: ChatOpenAI, docs: List[Document], summarize_length: int = 300, chain_type: str = "map_reduce"
    ) -> Tuple[str, float]:
        with st.spinner("Summarize Content ..."):
            # chain_typeでpromptを変える
            if chain_type == "map_reduce":
                map_prompt_template = self.prompts_loader.web_summarize_map_template()
                combine_prompt_template = self.prompts_loader.web_summarize_combine_template(summarize_length)
                MAP_PROMPT = PromptTemplate(template=map_prompt_template, input_variables=["text"])
                COMBINE_PROMPT = PromptTemplate(template=combine_prompt_template, input_variables=["text"])
                map_chain = LLMChain(llm=llm, prompt=MAP_PROMPT)
                reduce_chain = LLMChain(llm=llm, prompt=COMBINE_PROMPT)
                combine_documents_chain = StuffDocumentsChain(llm_chain=reduce_chain, document_variable_name="text")
                reduce_documents_chain = ReduceDocumentsChain(
                    combine_documents_chain=combine_documents_chain,
                    collapse_documents_chain=combine_documents_chain,
                    token_max=4000,
                )
                map_reduce_chain = MapReduceDocumentsChain(
                    llm_chain=map_chain,
                    reduce_documents_chain=reduce_documents_chain,
                    document_variable_name="text",
                    return_intermediate_steps=False,
                )
                response = map_reduce_chain.run(docs)
                answer = response
            elif chain_type == "map_rerank":
                st.write('"map_rerank" has not been implemented.')
                return None
            elif chain_type == "refine":
                prompt_template = self.prompts_loader.web_summarize_refine_template(summarize_length)
                PROMPT = PromptTemplate(template=prompt_template, input_variables=["text"])
                chain = load_summarize_chain(llm, chain_type=chain_type, verbose=True, refine_prompt=PROMPT)
                response = chain(
                    {"input_documents": docs, "token_max": self.sm.get_max_token()},
                    return_only_outputs=True,
                    # callbacks=[st_callback],
                )
                answer = response["output_text"]
            else:
                st.write("Please retry")
                return None

            token_cost_process = TokenCostProcess(llm.model_name)
            cost = token_cost_process.total_cost
            return answer, cost

    def render(self) -> None:
        llm = self.base_components()

        url_container = st.container()
        response_container = st.container()
        summarize_length = self.sidebar.slider("Summarize Length:", min_value=50, max_value=1000, value=300, step=1)
        chain_type = self.sidebar.radio("Choose chain type:", ("map_reduce", "map_rerank", "refine"))

        document = None
        with url_container:
            url = self.get_url_input()
            is_valid_url = self.validate_url(url)
            if not is_valid_url:
                st.write("Please input valid url")
            else:
                document = self.get_content(url)

        if document:
            with response_container:
                st.markdown("## Summary")
                answer, cost = self.summarize(llm, document, summarize_length, chain_type)
                self.sm.add_cost(cost)
                st.markdown(answer)
                st.markdown("---")
                st.markdown("## Original Text")
                stoggle("Original Text", document)

        # 合計コストの再取得、表示
        self.total_cost_component()
