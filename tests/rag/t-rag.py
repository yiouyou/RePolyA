import os
_RePolyA = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import sys
sys.path.append(_RePolyA)

from repolya._const import WORKSPACE_RAG
from repolya._log import logger_rag

from repolya.rag.digest_dir import dir_to_faiss_openai, get_files_from_dir
from repolya.rag.vdb_faiss import (
  get_faiss_OpenAI,
  show_faiss,
)


_dir = str(WORKSPACE_RAG / 'lj_rag')
_db_name = str(WORKSPACE_RAG / 'lj_rag_openai')
_clean_txt_dir = str(WORKSPACE_RAG / 'lj_rag_clean_txt')


if sys.argv[1] == 'show':
    show_faiss(get_faiss_OpenAI(_db_name))
elif sys.argv[1] == 'rerun':
    import shutil
    if os.path.exists(_db_name):
        shutil.rmtree(_db_name)
    if os.path.exists(_clean_txt_dir):
        shutil.rmtree(_clean_txt_dir)
    dir_to_faiss_openai(_dir, _db_name, _clean_txt_dir)
    show_faiss(get_faiss_OpenAI(_db_name))
else:
    print('Usage: python t-rag.py show/rerun')

