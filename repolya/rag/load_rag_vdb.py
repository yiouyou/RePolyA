from repolya._const import WORKSPACE_RAG

from repolya.rag.vdb_faiss import (
    get_faiss_OpenAI,
    get_faiss_HuggingFace,
)

_vdb_name = str(WORKSPACE_RAG / 'lj_rag_openai')
_vdb = get_faiss_OpenAI(_vdb_name)

