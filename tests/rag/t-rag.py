import os
_RePolyA = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import sys
sys.path.append(_RePolyA)

from repolya._const import WORKSPACE_RAG
from repolya._log import logger_rag

from repolya.rag.digest_dir import dir_to_faiss_openai, get_files_from_dir


_dir = str(WORKSPACE_RAG / 'lj_rag')
_vdb_name = str(WORKSPACE_RAG / 'lj_rag_openai')
_clean_txt_dir = str(WORKSPACE_RAG / 'lj_rag_clean_txt')

import shutil
if os.path.exists(_vdb_name):
    shutil.rmtree(_vdb_name)
if os.path.exists(_clean_txt_dir):
    shutil.rmtree(_clean_txt_dir)

dir_to_faiss_openai(_dir, _vdb_name, _clean_txt_dir)

