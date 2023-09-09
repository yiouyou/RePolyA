from repolya._log import logger_paper

from langchain.document_loaders import PyMuPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import FAISS
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.embeddings.openai import OpenAIEmbeddings

import os
import re


text_chunk_size = 3000
text_chunk_overlap = 300

##### docs
def get_docs_from_pdf(_fp):
    _f = os.path.basename(_fp)
    loader = PyMuPDFLoader(str(_fp))
    docs = loader.load()
    logger_paper.info(f"load {len(docs)} pages")
    return docs


##### split
def split_docs_recursive(_docs):
    ##### default list is ["\n\n", "\n", " ", ""]
    text_splitter = RecursiveCharacterTextSplitter(
        # Set a really small chunk size, just to show.
        chunk_size = text_chunk_size,
        chunk_overlap = text_chunk_overlap,
        length_function = len,
        is_separator_regex = False,
    )
    splited_docs = text_splitter.split_documents(_docs)
    return splited_docs


##### embedding
def embedding_to_faiss_ST(_docs, _db_name):
    ### all-mpnet-base-v2/all-MiniLM-L6-v2/all-MiniLM-L12-v2
    ### all-MiniLM-L12-v2
    _db_name_all = f"{_db_name}_all"
    _embedding_all = HuggingFaceEmbeddings(model_name="all-MiniLM-L12-v2")
    _db_all = FAISS.from_documents(_docs, _embedding_all)
    _db_all.save_local(_db_name_all)
    ### multi-qa-mpnet-base-dot-v1
    _db_name_multiqa = f"{_db_name}_multiqa"
    _embedding_multiqa = HuggingFaceEmbeddings(model_name="multi-qa-mpnet-base-dot-v1")
    _db_multiqa = FAISS.from_documents(_docs, _embedding_multiqa)
    _db_multiqa.save_local(_db_name_multiqa)
    ### log
    logger_paper.info(f"{_db_name_all}, {_db_name_multiqa}")
    logger_paper.info("[faiss save HuggingFaceEmbeddings embedding to disk]")

def embedding_to_faiss_OpenAI(_docs, _db_name):
    _embeddings = OpenAIEmbeddings()
    _db = FAISS.from_documents(_docs, _embeddings)
    _db.save_local(_db_name)
    logger_paper.info("/".join(_db_name.split("/")[-2:]))
    logger_paper.info("[faiss save OpenAI embedding to disk]")


##### faiss
def clean_txt(_txt):
    _1 = re.sub(r"\n+", "\n", _txt)
    _2 = re.sub(r"\t+\n", "\n", _1)
    _3 = re.sub(r" +\n", "\n", _2)
    _clean_txt = re.sub(r"\n+", "\n", _3)
    return _clean_txt

def pdf_to_faiss_OpenAI(_fp, _db_name):
    docs = get_docs_from_pdf(_fp)
    if len(docs) > 0:
        for doc in docs:
            doc.page_content = clean_txt(doc.page_content)
            # print(doc.metadata)
        logger_paper.info(f"docs: {len(docs)}")
        splited_docs = split_docs_recursive(docs)
        logger_paper.info(f"splited_docs: {len(splited_docs)}")
        embedding_to_faiss_OpenAI(splited_docs, _db_name)
    else:
        logger_paper.info("NO docs")

def pdf_to_faiss_ST(_fp, _db_name):
    docs = get_docs_from_pdf(_fp)
    if len(docs) > 0:
        for doc in docs:
            doc.page_content = clean_txt(doc.page_content)
            # print(doc.metadata)
        logger_paper.info(f"docs: {len(docs)}")
        splited_docs = split_docs_recursive(docs)
        logger_paper.info(f"splited_docs: {len(splited_docs)}")
        embedding_to_faiss_ST(splited_docs, _db_name)
    else:
        logger_paper.info("NO docs")

