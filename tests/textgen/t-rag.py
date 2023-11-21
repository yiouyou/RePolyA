import os
_RePolyA = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import sys
sys.path.append(_RePolyA)

from langchain.prompts import PromptTemplate
from langchain.output_parsers import PydanticOutputParser
from langchain.chains import LLMChain
from langchain.retrievers.multi_query import MultiQueryRetriever
from langchain.chains.question_answering import load_qa_chain
from langchain.callbacks.manager import CallbackManagerForRetrieverRun

from typing import List
from pydantic import BaseModel, Field

from repolya.local.textgen import get_textgen_llm
from repolya.rag.vdb_faiss import get_faiss_HuggingFace
from repolya.rag.qa_chain import pretty_print_docs

from repolya._const import WORKSPACE_RAG


_textgen_url = "http://127.0.0.1:5552"
llm = get_textgen_llm(_textgen_url, _top_p=0.1, _max_tokens=20000, _stopping_strings=[])

class LineList(BaseModel):
    # "lines" is the key (attribute name) of the parsed output
    lines: List[str] = Field(description="Lines of text")
class LineListOutputParser(PydanticOutputParser):
    def __init__(self) -> None:
        super().__init__(pydantic_object=LineList)
    def parse(self, text: str) -> LineList:
        lines = text.strip().split("\n")
        return LineList(lines=lines)
output_parser = LineListOutputParser()
QUERY_PROMPT = PromptTemplate(
        input_variables=["question"],
        template="""### System:

你是一名AI语言模型助手。
你的任务是生成五个给定用户问题的不同版本，用于从向量中检索相关文档数据库。
通过对用户问题产生多种观点，帮助用户克服了基于距离的相似性搜索的一些限制。
请提供这些替代问题，并用换行符分隔。

### Instruction:

原问题：{question}

### Response
""",
)


llm_chain = LLMChain(
    llm=llm,
    prompt=QUERY_PROMPT,
    output_parser=output_parser,
)

_db_name = str(WORKSPACE_RAG / 'lj_rag_hf')
_vdb = get_faiss_HuggingFace(_db_name)
_base_retriever = _vdb.as_retriever(search_kwargs={"k": 5})

_multi_retriever = MultiQueryRetriever(
    retriever=_base_retriever,
    llm_chain=llm_chain,
    parser_key="lines"
)

_query = "福特号舰长是谁？"

_run_manager = CallbackManagerForRetrieverRun.get_noop_manager()
_generated_queries = _multi_retriever.generate_queries(_query, _run_manager)
print(_generated_queries)

_docs = _multi_retriever.get_relevant_documents(_query)
print(pretty_print_docs(_docs))
exit()

_chain_type = 'stuff'
_qa = load_qa_chain(
    llm,
    chain_type=_chain_type
)

_ans = _qa(
    {
        "input_documents": _docs,
        "question": _query
    },
    return_only_outputs=True
)

print(_ans)


