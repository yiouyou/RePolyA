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


text_chunk_size = 1000
text_chunk_overlap = 50


def urls_to_faiss(_urls: list, _vdb_name: str, _clean_txt_dir: str):
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
        _new_metadata['title'] = _new_page_content.split('\n')[0]
        _new_metadata['description'] = ''
        _docs[i].page_content = _new_page_content
        _docs[i].metadata = _new_metadata
        _clean_out = os.path.join(_clean_txt_dir, f"{_new_metadata['title']}.txt")
        print(_clean_out)
        with open(_clean_out, 'w') as f:
            f.write(_new_page_content)
    _splited_docs = split_docs_recursive(_docs, text_chunk_size, text_chunk_overlap)
    if _vdb_name.endswith('_openai'):
        embedding_to_faiss_OpenAI(_splited_docs, _vdb_name)
    else:
        logger_rag.info(f"vdb_name '{_vdb_name}' is not ends with '_openai'")


