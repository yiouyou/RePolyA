from repolya._const import WORKSPACE_RAG
from repolya._log import logger_rag

from repolya.rag.doc_loader import clean_txt
from repolya.rag.doc_splitter import split_docs_recursive
from repolya.rag.vdb_faiss import (
    embedding_to_faiss_OpenAI,
    embedding_to_faiss_HuggingFace,
)
from repolya.toolset.load_web import load_urls_to_docs

import os
import re


text_chunk_size = 1000
text_chunk_overlap = 50


def clean_filename(text, max_length=10):
    # 移除非法文件名字符（例如: \ / : * ? " < > |）
    clean_text = re.sub(r'[\\/*?:"<>|]', '', text)
    # 替换操作系统敏感的字符
    clean_text = clean_text.replace(' ', '_')  # 替换空格为下划线
    # 取前 max_length 个字符作为文件名
    return clean_text[:max_length]


def urls_to_faiss_OpenAI(_urls: list, _db_name: str, _clean_txt_dir: str):
    if not os.path.exists(_clean_txt_dir):
        os.makedirs(_clean_txt_dir)
    _docs = load_urls_to_docs(_urls)
    for i in range(len(_docs)):
        _d = _docs[i].to_json()
        _page_content = _d['kwargs']['page_content']
        _new_page_content = clean_txt(_page_content)
        # print(f"'{_new_page_content}'")
        _metadata = _d['kwargs']['metadata']
        _new_metadata = {}
        _new_metadata['source'] = _metadata['source']
        _new_metadata['title'] = re.sub(r'[\s/]', '', _new_page_content)[:10]
        _new_metadata['description'] = ''
        _docs[i].page_content = _new_page_content
        _docs[i].metadata = _new_metadata
        _fn = clean_filename(_new_metadata['title'])
        _clean_out = os.path.join(_clean_txt_dir, f"{_fn}.txt")
        print(_clean_out)
        with open(_clean_out, 'w') as f:
            f.write(_new_page_content)
    text_chunk_size = 1000
    text_chunk_overlap = 100
    _splited_docs = split_docs_recursive(_docs, text_chunk_size, text_chunk_overlap)
    if not os.path.exists(_db_name):
        if _db_name.endswith('_openai'):
            embedding_to_faiss_OpenAI(_splited_docs, _db_name)
        else:
            logger_rag.info(f"db_name '{_db_name}' is not ends with '_openai'")
    else:
        logger_rag.error(f"db_name '{_db_name}' exists already.")


def urls_to_faiss_HuggingFace(_urls: list, _db_name: str, _clean_txt_dir: str):
    if not os.path.exists(_clean_txt_dir):
        os.makedirs(_clean_txt_dir)
    _docs = load_urls_to_docs(_urls)
    for i in range(len(_docs)):
        _d = _docs[i].to_json()
        _page_content = _d['kwargs']['page_content']
        _new_page_content = clean_txt(_page_content)
        # print(f"'{_new_page_content}'")
        _metadata = _d['kwargs']['metadata']
        _new_metadata = {}
        _new_metadata['source'] = _metadata['source']
        _new_metadata['title'] = re.sub(r'[\s/]', '', _new_page_content)[:10]
        _new_metadata['description'] = ''
        _docs[i].page_content = _new_page_content
        _docs[i].metadata = _new_metadata
        _fn = clean_filename(_new_metadata['title'])
        _clean_out = os.path.join(_clean_txt_dir, f"{_fn}.txt")
        print(_clean_out)
        with open(_clean_out, 'w') as f:
            f.write(_new_page_content)
    text_chunk_size = 1000
    text_chunk_overlap = 100
    _splited_docs = split_docs_recursive(_docs, text_chunk_size, text_chunk_overlap)
    if not os.path.exists(_db_name):
        if _db_name.endswith('_hf'):
            embedding_to_faiss_HuggingFace(_splited_docs, _db_name)
        else:
            logger_rag.info(f"db_name '{_db_name}' is not ends with '_hf'")
    else:
        logger_rag.error(f"db_name '{_db_name}' exists already.")

