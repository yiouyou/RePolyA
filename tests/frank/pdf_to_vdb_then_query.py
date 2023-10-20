import os
_RePolyA = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import sys
sys.path.append(_RePolyA)

from repolya._const import WORKSPACE_RAG
from repolya.rag.doc_loader import get_docs_from_pdf
from repolya.rag.doc_splitter import split_docs_recursive
from repolya.rag.vdb_faiss import (
    embedding_to_faiss_OpenAI,
    embedding_to_faiss_HuggingFace,
    get_faiss_OpenAI,
    get_faiss_HuggingFace,
)
from repolya.rag.qa_chain import (
    qa_vdb_multi_query,
    qa_docs_ensemble_query,
    qa_docs_parent_query,
)

import time


_pdf = str(WORKSPACE_RAG / "frank_doc.pdf")
_vdb_name_openai = str(WORKSPACE_RAG / "frank_doc_openai")
_vdb_name_huggingface = str(WORKSPACE_RAG / "frank_doc_huggingface")
text_chunk_size = 1000
text_chunk_overlap = 50

_docs = get_docs_from_pdf(_pdf)
_splited_docs = split_docs_recursive(_docs, text_chunk_size, text_chunk_overlap)

_splited_docs_list = []
for doc in _splited_docs:
    _splited_docs_list.append(doc.page_content)

if not os.path.exists(_vdb_name_openai):
    embedding_to_faiss_OpenAI(_splited_docs, _vdb_name_openai)
if not os.path.exists(_vdb_name_huggingface):
    embedding_to_faiss_HuggingFace(_splited_docs, _vdb_name_huggingface)

_query = sys.argv[1]

# start_time = time.time()
# _vdb_openai = get_faiss_OpenAI(_vdb_name_openai)
# _ans, _step, _token_cost = qa_vdb_multi_query(_query, _vdb_openai, 'stuff')
# print(f"ans_openai: {_ans}")
# # print(_token_cost)
# # print(f"step_openai: {_step}")
# end_time = time.time()
# execution_time = end_time - start_time
# print(f"Function took {execution_time:.5f} seconds to run.")


# start_time = time.time()
# _vdb_huggingface = get_faiss_HuggingFace(_vdb_name_huggingface)
# _ans, _step, _token_cost = qa_vdb_multi_query(_query, _vdb_huggingface, 'stuff')
# print(f"ans_huggingface: {_ans}")
# # print(_token_cost)
# # print(f"step_huggingface: {_step}")
# end_time = time.time()
# execution_time = end_time - start_time
# print(f"Function took {execution_time:.5f} seconds to run.")


# start_time = time.time()
# _ans, _step, _token_cost = qa_docs_ensemble_query(_query, _splited_docs_list, 'stuff')
# print(f"ans_ensemble: {_ans}")
# # print(_token_cost)
# # print(f"step_ensemble: {_step}")
# end_time = time.time()
# execution_time = end_time - start_time
# print(f"Function took {execution_time:.5f} seconds to run.")


start_time = time.time()
_ans, _step, _token_cost = qa_docs_parent_query(_query, _splited_docs, 'stuff')
print(f"ans_parent: {_ans}")
# print(_token_cost)
# print(f"step_parent: {_step}")
end_time = time.time()
execution_time = end_time - start_time
print(f"Function took {execution_time:.5f} seconds to run.")

