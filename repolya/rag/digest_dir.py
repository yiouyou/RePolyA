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


def calculate_md5(_fp):
    hash_md5 = hashlib.md5()
    with open(_fp, "rb") as f:
        # 以块为单位读取文件，以便适应大文件
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def str_to_sha256(_str):
    """Convert a string to its SHA-256 hash."""
    sha256_hash = hashlib.sha256()
    sha256_hash.update(_str.encode('utf-8'))
    return sha256_hash.hexdigest()


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


def dir_to_faiss_OpenAI(_dir: str, _db_name: str, _clean_txt_dir: str):
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
        # print(f"'{_doc[0].page_content}'")
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
    logger_rag.info(f"load {len(_DOCs)} docs from '{_dir}'")
    _clean_DOCs = []
    for i in range(len(_DOCs)):
        _d = _DOCs[i].to_json()
        _page_content = _d['kwargs']['page_content']
        _new_page_content = clean_txt(_page_content)
        _metadata = _d['kwargs']['metadata']
        _new_metadata = {}
        _new_metadata['source'] = _metadata['source']
        _source_fn = os.path.splitext(os.path.basename(_metadata['source']))[0]
        ### title: 前10个非空字符
        _new_metadata['title'] = f"{_source_fn}, " + re.sub(r'[\s/]', '', _new_page_content)[:10]
        # print(_new_metadata['source'])
        # print(_source_fn)
        # print(_new_metadata['title'])
        _new_metadata['description'] = ''
        _DOCs[i].page_content = _new_page_content
        _DOCs[i].metadata = _new_metadata
        # _clean_file = str_to_sha256(_new_page_content.split('\n')[0]) + ".txt"
        _clean_file = _new_metadata['title'] + ".txt"
        # logger_rag.info(f"write '{_clean_file}'")
        _clean_out = os.path.join(_clean_txt_dir, _clean_file)
        if _new_page_content != '':
            with open(_clean_out, 'w') as f:
                f.write(f"{_new_metadata['title']}\n\n'{_new_page_content}'")
            _clean_DOCs.append(_DOCs[i])
        else:
            logger_rag.info(f"empty doc '{_clean_file}'")
    text_chunk_size = 500
    text_chunk_overlap = 50
    _splited_docs = split_docs_recursive(_clean_DOCs, text_chunk_size, text_chunk_overlap)
    if not os.path.exists(_db_name):
        if _db_name.endswith('_openai'):
            embedding_to_faiss_OpenAI(_splited_docs, _db_name)
        else:
            logger_rag.info(f"db_name '{_db_name}' is not ends with '_openai'")
    else:
        logger_rag.error(f"db_name '{_db_name}' exists already.")


def dir_to_faiss_HuggingFace(_dir: str, _db_name: str, _clean_txt_dir: str):
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
        # print(f"'{_doc[0].page_content}'")
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
    logger_rag.info(f"load {len(_DOCs)} docs from '{_dir}'")
    _clean_DOCs = []
    for i in range(len(_DOCs)):
        _d = _DOCs[i].to_json()
        _page_content = _d['kwargs']['page_content']
        _new_page_content = _page_content #clean_txt(_page_content)
        _metadata = _d['kwargs']['metadata']
        _new_metadata = {}
        _new_metadata['source'] = _metadata['source']
        _source_fn = os.path.splitext(os.path.basename(_metadata['source']))[0]
        ### title: 前10个非空字符
        _new_metadata['title'] = f"{_source_fn}, " + re.sub(r'[\s/]', '', _new_page_content)[:10]
        # print(_new_metadata['source'])
        # print(_source_fn)
        # print(_new_metadata['title'])
        _new_metadata['description'] = ''
        _DOCs[i].page_content = _new_page_content
        _DOCs[i].metadata = _new_metadata
        # _clean_file = str_to_sha256(_new_page_content.split('\n')[0]) + ".txt"
        _clean_file = _new_metadata['title'] + ".txt"
        # logger_rag.info(f"write '{_clean_file}'")
        _clean_out = os.path.join(_clean_txt_dir, _clean_file)
        if _new_page_content != '':
            with open(_clean_out, 'w') as f:
                f.write(f"{_new_metadata['title']}\n\n'{_new_page_content}'")
            _clean_DOCs.append(_DOCs[i])
        else:
            logger_rag.info(f"empty doc '{_clean_file}'")
    text_chunk_size = 1000
    text_chunk_overlap = 100
    _splited_docs = split_docs_recursive(_clean_DOCs, text_chunk_size, text_chunk_overlap)
    if not os.path.exists(_db_name):
        if _db_name.endswith('_hf'):
            embedding_to_faiss_HuggingFace(_splited_docs, _db_name)
        else:
            logger_rag.info(f"db_name '{_db_name}' is not ends with '_hf'")
    else:
        logger_rag.error(f"db_name '{_db_name}' exists already.")

