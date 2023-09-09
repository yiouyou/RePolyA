from repolya._log import logger_paper

from langchain import LLMChain
from langchain.llms import OpenAI
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.output_parsers import PydanticOutputParser

from langchain.retrievers import ContextualCompressionRetriever
from langchain.retrievers.multi_query import MultiQueryRetriever
from langchain.retrievers.merger_retriever import MergerRetriever
from langchain.retrievers.document_compressors import DocumentCompressorPipeline

from langchain.document_transformers import (
    LongContextReorder,
    EmbeddingsRedundantFilter,
    EmbeddingsClusteringFilter,
)
from langchain.chains import (
    RetrievalQA,
    RetrievalQAWithSourcesChain,
    StuffDocumentsChain,
)
from langchain.callbacks import get_openai_callback
from langchain.callbacks.manager import (
    AsyncCallbackManagerForRetrieverRun,
    CallbackManagerForRetrieverRun,
)

from langchain.vectorstores import FAISS
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.embeddings.openai import OpenAIEmbeddings

from typing import List
from pydantic import BaseModel, Field
import os


def pretty_print_docs(docs):
    # _pretty = f"\n{'-' * 100}\n".join([f"Document {i+1}:\n\n" + d.page_content for i, d in enumerate(docs)])
    _doc = []
    _doc_meta = []
    for i, doc in enumerate(docs):
        _doc.append(f"Document {i+1}:\n\n" + str(doc.metadata) + "\n\n" + doc.page_content)
        _doc_meta.append(f"Document {i+1}:\n\n" + str(doc.metadata)+ "\n" + str(len(doc.page_content)))
    _pretty = f"\n{'-' * 100}\n".join(_doc)
    # print(_pretty)
    _meta = f"\n{'-' * 100}\n".join(_doc_meta)
    # print(_meta)
    return _pretty


##### OpenAI retriever
def get_faiss_OpenAI(_db_name):
    _embeddings = OpenAIEmbeddings()
    _db = FAISS.load_local(_db_name, _embeddings)
    return _db

def get_faiss_OpenAI_multi_query_retriever(_db_name):
    class LineList(BaseModel):
        # "lines" is the key (attribute name) of the parsed output
        lines: List[str] = Field(description="Lines of text")

    class LineListOutputParser(PydanticOutputParser):
        def __init__(self) -> None:
            super().__init__(pydantic_object=LineList)
        def parse(self, text: str) -> LineList:
            lines = text.strip().split("\n")
            return LineList(lines=lines)
    output_parser = LineListOutputParser()
    
    QUERY_PROMPT = PromptTemplate(
        input_variables=["question"],
        template="""You are an AI language model assistant. Your task is to generate five 
different versions of the given user question to retrieve relevant documents from a vector 
database. By generating multiple perspectives on the user question, your goal is to help
the user overcome some of the limitations of the distance-based similarity search. 
Provide these alternative questions seperated by newlines.
Original question: {question}""",
    )
    llm = ChatOpenAI(model_name=os.getenv('OPENAI_LLM_MODEL'), temperature=0)
    llm_chain = LLMChain(llm=llm, prompt=QUERY_PROMPT, output_parser=output_parser)
    _db = get_faiss_OpenAI(_db_name)
    _base_retriever = _db.as_retriever()
    _multi_retriever = MultiQueryRetriever(
        retriever=_base_retriever,
        llm_chain=llm_chain,
        parser_key="lines"
    )
    return _multi_retriever

def qa_faiss_OpenAI_multi_query(_query, _db_name):
    _ans, _steps = "", ""
    llm = ChatOpenAI(model_name=os.getenv('OPENAI_LLM_MODEL'), temperature=0)
    with get_openai_callback() as cb:
        _retriever = get_faiss_OpenAI_multi_query_retriever(_db_name)
        _run_manager = CallbackManagerForRetrieverRun.get_noop_manager()
        _generated_queries = _retriever.generate_queries(_query, _run_manager)
        logger_paper.info(_generated_queries)
        ##### _docs, _reordered_docs
        _docs = _retriever.get_relevant_documents(_query)
        _reordering = LongContextReorder()
        _reordered_docs = _reordering.transform_documents(_docs)
        _pretty_docs = pretty_print_docs(_docs)
        _pretty_reordered_docs = pretty_print_docs(_reordered_docs)
        #####
        document_prompt = PromptTemplate(
            input_variables=["page_content"], template="{page_content}"
        )
        stuff_prompt_override = """Given this text extracts:
-----
{context}
-----
Please answer the following question:
{query}"""
        prompt = PromptTemplate(
            template=stuff_prompt_override, input_variables=["context", "query"]
        )
        llm_chain = LLMChain(
            llm=llm,
            prompt=prompt
        )
        _qa_chain = StuffDocumentsChain(
            llm_chain=llm_chain,
            document_prompt=document_prompt,
            document_variable_name="context",
        )
        _ans = _qa_chain.run(
            query=_query,
            input_documents=_reordered_docs
        )
        #####
        _token_cost = f"Tokens: {cb.total_tokens} = (Prompt {cb.prompt_tokens} + Completion {cb.completion_tokens}) Cost: ${format(cb.total_cost, '.5f')}"
        # print(_token_cost)
        _steps = f"{_token_cost}\n\n"+ "\n".join(_generated_queries)
        # _steps += f"\n\n{'=' * 100}docs\n" + _pretty_docs
        _steps += f"\n\n{'=' * 60} reordered_docs\n" + _pretty_reordered_docs
        logger_paper.info(f"{_ans}")
        logger_paper.info(f"{_token_cost}")
        logger_paper.debug(f"{_steps}")
    return [_ans, _steps]


##### ST retriever
def get_faiss_ST(_db_name):
    ### all-MiniLM-L12-v2
    _db_name_all = os.path.join(_db_name, 'all-MiniLM-L12-v2')
    _embedding_all = HuggingFaceEmbeddings(model_name="all-MiniLM-L12-v2")
    _db_all = FAISS.load_local(_db_name_all, _embedding_all)
    ### multi-qa-mpnet-base-dot-v1
    _db_name_multiqa = os.path.join(_db_name, 'multi-qa-mpnet-base-dot-v1')
    _embedding_multiqa = HuggingFaceEmbeddings(model_name="multi-qa-mpnet-base-dot-v1")
    _db_multiqa = FAISS.load_local(_db_name_multiqa, _embedding_multiqa)
    return _db_all, _db_multiqa

def get_faiss_ST_multi_query_retriever(_db_name):
    class LineList(BaseModel):
        # "lines" is the key (attribute name) of the parsed output
        lines: List[str] = Field(description="Lines of text")

    class LineListOutputParser(PydanticOutputParser):
        def __init__(self) -> None:
            super().__init__(pydantic_object=LineList)
        def parse(self, text: str) -> LineList:
            lines = text.strip().split("\n")
            return LineList(lines=lines)
    output_parser = LineListOutputParser()
    
    QUERY_PROMPT = PromptTemplate(
        input_variables=["question"],
        template="""You are an AI language model assistant. Your task is to generate five 
different versions of the given user question to retrieve relevant documents from a vector 
database. By generating multiple perspectives on the user question, your goal is to help
the user overcome some of the limitations of the distance-based similarity search. 
Provide these alternative questions seperated by newlines.
Original question: {question}""",
    )
    llm = ChatOpenAI(model_name=os.getenv('OPENAI_LLM_MODEL'), temperature=0)
    llm_chain = LLMChain(llm=llm, prompt=QUERY_PROMPT, output_parser=output_parser)
    filter_embeddings = OpenAIEmbeddings()
    ##### 
    _db_all, _db_multiqa = get_faiss_ST(_db_name)
    _retriever_all = _db_all.as_retriever(
        search_type="similarity",
        search_kwargs={"k": 5, "include_metadata": True}
    )
    _retriever_multiqa = _db_multiqa.as_retriever(
        search_type="mmr",
        search_kwargs={"k": 5, "include_metadata": True}
    )
    _lotr = MergerRetriever(retrievers=[_retriever_all, _retriever_multiqa])
    ##### Remove redundant results from the merged retrievers
    _filter = EmbeddingsRedundantFilter(embeddings=filter_embeddings)
    ##### Re-order results to avoid performance degradation
    _reordering = LongContextReorder()
    ##### ContextualCompressionRetriever
    _pipeline = DocumentCompressorPipeline(transformers=[_filter, _reordering])
    _compression_retriever_reordered = ContextualCompressionRetriever(
        base_compressor=_pipeline,
        base_retriever=_lotr
    )
    ##### MultiQueryRetriever
    _multi_retriever = MultiQueryRetriever(
        retriever=_compression_retriever_reordered,
        llm_chain=llm_chain,
        parser_key="lines"
    )
    return _multi_retriever

def qa_faiss_ST_multi_query(_query, _db_name):
    _ans, _steps = "", ""
    llm = ChatOpenAI(model_name=os.getenv('OPENAI_LLM_MODEL'), temperature=0)
    with get_openai_callback() as cb:
        _retriever = get_faiss_ST_multi_query_retriever(_db_name)
        _run_manager = CallbackManagerForRetrieverRun.get_noop_manager()
        _generated_queries = _retriever.generate_queries(_query, _run_manager)
        logger_paper.info(_generated_queries)
        ##### _docs
        _docs = _retriever.get_relevant_documents(_query)
        _pretty_docs = pretty_print_docs(_docs)
        #####
        _qa_chain = RetrievalQAWithSourcesChain.from_chain_type(
            llm,
            chain_type="map_reduce", # stuff, map_reduce, refine, map_rerank
            retriever=_retriever
        )
        _ans = _qa_chain(
            {"question": _query},
            return_only_outputs=False
        )
        #####
        _token_cost = f"Tokens: {cb.total_tokens} = (Prompt {cb.prompt_tokens} + Completion {cb.completion_tokens}) Cost: ${format(cb.total_cost, '.5f')}"
        # print(_token_cost)
        _steps = f"{_token_cost}\n\n"+ "\n".join(_generated_queries)
        _steps += f"\n\n{'=' * 60} docs\n" + _pretty_docs
        logger_paper.info(f"{_ans}")
        logger_paper.info(f"{_token_cost}")
        logger_paper.debug(f"{_steps}")
    return [_ans, _steps]

