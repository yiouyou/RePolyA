from repolya._const import WORKSPACE_RAG
from repolya._log import logger_rag

from repolya.rag.doc_loader import clean_txt
from repolya.rag.doc_splitter import split_docs_recursive
from repolya.rag.vdb_faiss import (
    embedding_to_faiss_OpenAI,
    embedding_to_faiss_HuggingFace,
)
from repolya.toolset.load_file import (
    load_txt_to_docs,
    load_pdf_to_docs,
    load_md_to_docs,
    load_html_to_docs,
    load_py_to_docs,
    load_csv_to_docs,
    load_docx_to_docs,
    load_pptx_to_docs,
    load_eml_to_docs,
)

import os
import re
import hashlib


text_chunk_size = 1000
text_chunk_overlap = 50


def get_files_from_dir(_dir, _ext):
    """递归从指定目录中获取具有给定扩展名的文件的路径。
    Args:
    _dir (str): 要搜索的目录的路径。
    _ext (list): 要搜索的文件的扩展名列表，例如 ['.txt', '.pdf']。
    Returns:
    list: 具有指定扩展名的文件的路径列表。
    """
    _files = []
    # os.walk 生成目录树中的文件名
    for root, dirs, files in os.walk(_dir):
        for file in files:
            # 检查文件扩展名是否在我们的扩展名列表中
            if any(file.endswith(ext) for ext in _ext):
                full_path = os.path.join(root, file)
                _files.append(full_path)
    return _files


def str_to_sha256(_str):
    """Convert a string to its SHA-256 hash."""
    sha256_hash = hashlib.sha256()
    sha256_hash.update(_str.encode('utf-8'))
    return sha256_hash.hexdigest()


def dir_to_faiss_openai(_dir: str, _vdb_name: str, _clean_txt_dir: str):
    if not os.path.exists(_clean_txt_dir):
        os.makedirs(_clean_txt_dir)
    _DOCs = []
    # _csv_files = get_files_from_dir(_dir, ['.csv'])
    _txt_files = get_files_from_dir(_dir, ['.txt'])
    _pdf_files = get_files_from_dir(_dir, ['.pdf'])
    _md_files = get_files_from_dir(_dir, ['.md'])
    _html_files = get_files_from_dir(_dir, ['.html'])
    _py_files = get_files_from_dir(_dir, ['.py'])
    _docx_files = get_files_from_dir(_dir, ['.docx', '.doc'])
    _pptx_files = get_files_from_dir(_dir, ['.pptx', '.ppt'])
    _eml_files = get_files_from_dir(_dir, ['.eml', '.msg'])
    for i in _txt_files:
        _doc = load_txt_to_docs(i)
        _DOCs.extend(_doc)
    for i in _pdf_files:
        _doc = load_pdf_to_docs(i)
        _DOCs.extend(_doc)
    for i in _md_files:
        _doc = load_md_to_docs(i)
        _DOCs.extend(_doc)
    for i in _html_files:
        _doc = load_html_to_docs(i)
        _DOCs.extend(_doc)
    for i in _py_files:
        _doc = load_py_to_docs(i)
        _DOCs.extend(_doc)
    for i in _docx_files:
        _doc = load_docx_to_docs(i)
        _DOCs.extend(_doc)
    for i in _pptx_files:
        _doc = load_pptx_to_docs(i)
        _DOCs.extend(_doc)
    for i in _eml_files:
        _doc = load_eml_to_docs(i)
        _DOCs.extend(_doc)
    ### docs -> faiss
    if len(_DOCs) == 0:
        logger_rag.error(f"NO docs found in dir '{_dir}'")
        return
    logger_rag.info(f"Find {len(_DOCs)} docs in dir '{_dir}'")
    for i in range(len(_DOCs)):
        _d = _DOCs[i].to_json()
        _page_content = _d['kwargs']['page_content']
        _new_page_content = clean_txt(_page_content)
        _metadata = _d['kwargs']['metadata']
        _new_metadata = {}
        _new_metadata['source'] = _metadata['source']
        _source_fn = os.path.splitext(os.path.basename(_metadata['source']))[0]
        ### title: 前10个非空字符
        _new_metadata['title'] = f"{_source_fn}, " + re.sub('\s', '', _new_page_content)[:10]
        # print(_new_metadata['source'])
        # print(_source_fn)
        # print(_new_metadata['title'])
        _new_metadata['description'] = ''
        _DOCs[i].page_content = _new_page_content
        _DOCs[i].metadata = _new_metadata
        _clean_file = str_to_sha256(_new_page_content.split('\n')[0]) + ".txt"
        # logger_rag.info(f"write '{_clean_file}'")
        _clean_out = os.path.join(_clean_txt_dir, _clean_file)
        with open(_clean_out, 'w') as f:
            f.write(_new_page_content)
    _splited_docs = split_docs_recursive(_DOCs, text_chunk_size, text_chunk_overlap)
    if _vdb_name.endswith('_openai'):
        embedding_to_faiss_OpenAI(_splited_docs, _vdb_name)
    else:
        logger_rag.info(f"vdb_name '{_vdb_name}' is not ends with '_openai'")

