from repolya._log import logger_rag

from repolya.rag.doc_loader import get_docs_from_pdf
from repolya.rag.doc_splitter import split_docs_recursive
from repolya.rag.embedding import get_embedding_OpenAI, get_embedding_HuggingFace

from langchain.vectorstores import FAISS

import os


##### OpenAI
def embedding_to_faiss_OpenAI(_docs, _db_name):
    _model_name, _embedding = get_embedding_OpenAI()
    _vdb_name = os.path.join(_db_name, _model_name)
    if not os.path.exists(_vdb_name):
        _db = FAISS.from_documents(_docs, _embedding)
        _db.save_local(_vdb_name)
        logger_rag.info("/".join(_vdb_name.split("/")[-2:]))
    ### log
    logger_rag.info(f"save {_model_name} embedding to faiss {_vdb_name}")


def pdf_to_faiss_OpenAI(_fp, _db_name, text_chunk_size=3000, text_chunk_overlap=300):
    docs = get_docs_from_pdf(_fp)
    if len(docs) > 0:
        logger_rag.info(f"docs: {len(docs)}")
        splited_docs = split_docs_recursive(docs, text_chunk_size, text_chunk_overlap)
        logger_rag.info(f"splited_docs: {len(splited_docs)}")
        embedding_to_faiss_OpenAI(splited_docs, _db_name)
    else:
        logger_rag.info("NO docs")


def get_faiss_OpenAI(_db_name):
    _model_name, _embedding = get_embedding_OpenAI()
    _vdb_name = os.path.join(_db_name, _model_name)
    if os.path.exists(_vdb_name):
        _vdb = FAISS.load_local(_vdb_name, _embedding)
        logger_rag.info(f"load {_model_name} embedding from faiss {_vdb_name}")
        return _vdb
    else:
        logger_rag.info(f"NO {_vdb_name}")
        return None


##### HuggingFace
def embedding_to_faiss_HuggingFace(_docs, _db_name):
    _model_name, _embedding = get_embedding_HuggingFace()
    _vdb_name = os.path.join(_db_name, _model_name)
    if not os.path.exists(_vdb_name):
        _vdb = FAISS.from_documents(_docs, _embedding)
        _vdb.save_local(_vdb_name)
        logger_rag.info("/".join(_vdb_name.split("/")[-2:]))
    ### log
    logger_rag.info(f"save {_model_name} embedding to faiss {_vdb_name}")


def pdf_to_faiss_HuggingFace(_fp, _db_name, text_chunk_size=3000, text_chunk_overlap=300):
    docs = get_docs_from_pdf(_fp)
    if len(docs) > 0:
        logger_rag.info(f"docs: {len(docs)}")
        splited_docs = split_docs_recursive(docs, text_chunk_size, text_chunk_overlap)
        logger_rag.info(f"splited_docs: {len(splited_docs)}")
        embedding_to_faiss_HuggingFace(splited_docs, _db_name)
    else:
        logger_rag.info("NO docs")


def get_faiss_HuggingFace(_db_name):
    _model_name, _embedding = get_embedding_HuggingFace()
    _vdb_name = os.path.join(_db_name, _model_name)
    if os.path.exists(_vdb_name):
        _vdb = FAISS.load_local(_vdb_name, _embedding)
        logger_rag.info(f"load {_model_name} embedding from faiss {_vdb_name}")
        return _vdb
    else:
        logger_rag.info(f"NO {_vdb_name}")
        return None

