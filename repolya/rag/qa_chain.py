from repolya._log import logger_rag

from langchain.llms import OpenAI
from langchain.chat_models import ChatOpenAI
from langchain.chains import (
    LLMChain,
    RetrievalQA,
    RetrievalQAWithSourcesChain,
    StuffDocumentsChain,
)
from langchain.document_loaders import TextLoader
from langchain.chains.question_answering import load_qa_chain
from langchain.chains.summarize import load_summarize_chain
from langchain.callbacks import get_openai_callback
from langchain.callbacks.manager import (
    AsyncCallbackManagerForRetrieverRun,
    CallbackManagerForRetrieverRun,
)

from repolya.rag.retriever import (
    get_vdb_multi_query_retriever,
    get_docs_ensemble_retriever,
    get_docs_parent_retriever,
)


def pretty_print_docs(docs):
    # _pretty = f"\n{'-' * 100}\n".join([f"Document {i+1}:\n\n" + d.page_content for i, d in enumerate(docs)])
    _doc = []
    _doc_meta = []
    for i, doc in enumerate(docs):
        _doc.append(f"Document {i+1}:\n\n" + str(doc.metadata) + "\n\n" + doc.page_content)
        _doc_meta.append(f"Document {i+1}:\n\n" + str(doc.metadata)+ "\n" + str(len(doc.page_content)))
    _pretty = f"\n{'-' * 60}\n".join(_doc)
    # print(_pretty)
    _meta = f"\n{'-' * 60}\n".join(_doc_meta)
    # print(_meta)
    return _pretty


##### Multi Query
def qa_vdb_multi_query(_query, _vdb, _chain_type):
    if _chain_type not in ['stuff', 'map_reduce', 'refine', 'map_rerank']:
        logger_rag.error("_chain_type must be one of 'stuff', 'map_reduce', 'refine', or 'map_rerank'")
    _ans, _steps, _token_cost = "", "", ""
    llm = ChatOpenAI(model_name="gpt-3.5-turbo-16k", temperature=0)
    with get_openai_callback() as cb:
        _multi_retriever = get_vdb_multi_query_retriever(_vdb)
        ##### _docs
        _docs = _multi_retriever.get_relevant_documents(_query)
        #####
        _qa = load_qa_chain(
            llm,
            chain_type=_chain_type
        )
        _ans = _qa(
            {
                "input_documents": _docs,
                "question": _query
            },
            return_only_outputs=True
        )
        #####
        _token_cost = f"Tokens: {cb.total_tokens} = (Prompt {cb.prompt_tokens} + Completion {cb.completion_tokens}) Cost: ${format(cb.total_cost, '.5f')}"
        # print(_token_cost)
        _run_manager = CallbackManagerForRetrieverRun.get_noop_manager()
        _generated_queries = _multi_retriever.generate_queries(_query, _run_manager)
        logger_rag.info(f"Q: {_query}")
        for i in _generated_queries:
            logger_rag.info(i)
        _steps = "\n".join(_generated_queries)
        _steps += f"\n\n{'=' * 40}docs\n" + pretty_print_docs(_docs)
        logger_rag.info(f"A: {_ans['output_text']}")
        logger_rag.info(f"[{_chain_type}] {_token_cost}")
        logger_rag.debug(f"[{_chain_type}] {_steps}")
    return [_ans['output_text'], _steps, _token_cost]


##### Ensemble
def qa_docs_ensemble_query(_query, _docs, _chain_type):
    if _chain_type not in ['stuff', 'map_reduce', 'refine', 'map_rerank']:
        logger_rag.error("_chain_type must be one of 'stuff', 'map_reduce', 'refine', or 'map_rerank'")
    _ans, _steps, _token_cost = "", "", ""
    llm = ChatOpenAI(model_name="gpt-3.5-turbo-16k", temperature=0)
    with get_openai_callback() as cb:
        _ensemble_retriever = get_docs_ensemble_retriever(_docs)
        ##### _docs
        _docs = _ensemble_retriever.get_relevant_documents(_query)
        #####
        _qa = load_qa_chain(
            llm,
            chain_type=_chain_type
        )
        _ans = _qa(
            {
                "input_documents": _docs,
                "question": _query
            },
            return_only_outputs=True
        )
        #####
        _token_cost = f"Tokens: {cb.total_tokens} = (Prompt {cb.prompt_tokens} + Completion {cb.completion_tokens}) Cost: ${format(cb.total_cost, '.5f')}"
        # print(_token_cost)
        _steps = f"\n\n{'=' * 40}docs\n" + pretty_print_docs(_docs)
        logger_rag.info(f"A: {_ans['output_text']}")
        logger_rag.info(f"[{_chain_type}] {_token_cost}")
        logger_rag.debug(f"[{_chain_type}] {_steps}")
    return [_ans['output_text'], _steps, _token_cost]


##### Parent Document
def qa_docs_parent_query(_query, _docs, _chain_type):
    if _chain_type not in ['stuff', 'map_reduce', 'refine', 'map_rerank']:
        logger_rag.error("_chain_type must be one of 'stuff', 'map_reduce', 'refine', or 'map_rerank'")
    _ans, _steps, _token_cost = "", "", ""
    llm = ChatOpenAI(model_name="gpt-3.5-turbo-16k", temperature=0)
    with get_openai_callback() as cb:
        _parent_retriever = get_docs_parent_retriever(_docs)
        ##### _docs
        _docs = _parent_retriever.get_relevant_documents(_query)
        #####
        _qa = load_qa_chain(
            llm,
            chain_type=_chain_type
        )
        _ans = _qa(
            {
                "input_documents": _docs,
                "question": _query
            },
            return_only_outputs=True
        )
        #####
        _token_cost = f"Tokens: {cb.total_tokens} = (Prompt {cb.prompt_tokens} + Completion {cb.completion_tokens}) Cost: ${format(cb.total_cost, '.5f')}"
        # print(_token_cost)
        _steps = f"\n\n{'=' * 40}docs\n" + pretty_print_docs(_docs)
        logger_rag.info(f"A: {_ans['output_text']}")
        logger_rag.info(f"[{_chain_type}] {_token_cost}")
        logger_rag.debug(f"[{_chain_type}] {_steps}")
    return [_ans['output_text'], _steps, _token_cost]


##### summerize the qa ans txt file
def qa_summerize(_txt_fp: str, _chain_type: str):
    docs = TextLoader(_txt_fp).load()
    llm = ChatOpenAI(temperature=0, model_name="gpt-3.5-turbo")
    with get_openai_callback() as cb:
        chain = load_summarize_chain(llm, chain_type=_chain_type)
        _sum = chain.run(docs)
        _token_cost = f"Tokens: {cb.total_tokens} = (Prompt {cb.prompt_tokens} + Completion {cb.completion_tokens}) Cost: ${format(cb.total_cost, '.5f')}"
        logger_rag.info(f"summarize: {_sum}")
        logger_rag.info(f"[{_chain_type}] {_token_cost}")
    return [_sum, _token_cost]

