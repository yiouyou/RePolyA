from langchain.document_loaders.merge import MergedDataLoader

from langchain.docstore.document import Document
from typing import List


def parse_intermediate_steps(_list):
    _steps = []
    for n in range(len(_list)):
        i = _list[n]
        i_str = f"Step {n+1}: {i[0].tool}\n"
        i_str += f"> {i[0].tool_input}\n"
        i_str += f"< {i[0].log}\n"
        i_str += f"# {i[1]}\n"
        _steps.append(i_str)
    return "\n".join(_steps)


def merge_doc_loader(_list: List[Document]):
    loader_all = MergedDataLoader(loaders=_list)
    docs_all = loader_all.load()
    return docs_all

